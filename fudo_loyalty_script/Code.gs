// ============================================================
//  FUDO → SUPABASE  |  Google Apps Script
//  Kingdom Coffee – Sync de ventas (solo para respaldo/API)
//  Actualizado: 2026-03-02
//
//  ⚠ NOTA IMPORTANTE SOBRE LA ESTRATEGIA DE MATCH:
//  Fudo NO guarda teléfonos de clientes en las ventas.
//  Por eso el flujo PRINCIPAL es:
//    Cajero escanea QR del cliente en la app → StaffDashboard → Supabase
//
//  Este script solo sirve como RESPALDO para registrar
//  la venta en Supabase cuando se tiene el ID de Fudo,
//  sin intentar hacer match automático con un cliente.
//  Los puntos quedan "pendientes" hasta que el staff
//  confirma el cliente con el QR.
// ============================================================


// ============================================================
//  SECCIÓN 1 – CONFIGURACIÓN  (⬅ solo cambia aquí)
// ============================================================

// --- Credenciales Fudo ---
var FUDO_USER     = 'automati...';   // ← Tu usuario de Fudo
var FUDO_PASSWORD = 'automati...';   // ← Tu contraseña de Fudo

// --- Bearer token de la API de Fudo (ya lo tienes!) ---
// Obtenido de test_fudo_v1.py — úsalo directamente si el login por form falla
var FUDO_BEARER = 'eyJhbGciOiJIUzI1NiJ9.eyJhaSI6MTkxNDczLCJ1aSI6MzYsImV4cCI6MTc3MDg2Njg0MX0.QtDb4t3v5SLP9jXTEGOJegSBhegc7a34dya_VgPDdek';

// --- URLs Fudo ---
var FUDO_LOGIN_URL      = 'https://app-v2.fu.do/login/';
var FUDO_SALES_API_URL  = 'https://api.fu.do/v1/orders'; // Ajusta según testEndpointsAlternativos()

// --- Supabase (ya configurado en tu proyecto!) ---
var SUPABASE_URL     = 'https://bcfulknkkwlpxpiuboyt.supabase.co';
var SUPABASE_KEY     = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjZnVsa25ra3dscHhwaXVib3l0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTE1NDA4NCwiZXhwIjoyMDg2NzMwMDg0fQ.Yt10YQKSQjaqwy8vCgWItxkyQ7aaxMUW-7p1a7XEQ9Y';

// --- Regla de puntos ---
var PESOS_POR_PUNTO = 10000;  // 1 punto por cada $10.000 CLP


// ============================================================
//  SECCIÓN 2 – MAPEO DE CAMPOS DE FUDO
//  ⬅ Ajusta estos nombres cuando veas el JSON real en los logs
// ============================================================
var CAMPO_ID_VENTA          = 'id';
var CAMPO_MONTO             = 'total';
var CAMPO_FECHA             = 'closedAt';       // o 'createdAt', 'date'
var CAMPO_CUSTOMER          = 'customer';        // objeto cliente dentro de la venta
var CAMPO_NOMBRE_CUSTOMER   = 'name';           // nombre del cliente
var CAMPO_EMAIL_CUSTOMER    = 'email';          // email del cliente (si existe)
var CAMPO_PHONE_CUSTOMER    = 'phone';          // teléfono del cliente (si existe)


// ============================================================
//  SECCIÓN 3 – FUNCIÓN PRINCIPAL
// ============================================================

/**
 * Función principal – ejecutada por el trigger cada 15 min.
 * Obtiene ventas de Fudo y las registra en Supabase.
 * NOTA: las ventas quedan sin user_id (sin match de cliente)
 * porque Fudo no lo expone. El staff las vincula con el QR.
 */
function procesarVentasFudo() {
  Logger.log('====== INICIO procesarVentasFudo ======');
  Logger.log('Hora: ' + new Date().toISOString());

  try {
    // 1. Obtener ventas (primero intentamos con Bearer directo)
    var ventas = fetchSalesConBearer_();

    // Si el Bearer falló intentamos con login por formulario
    if (ventas === null) {
      Logger.log('Bearer falló, intentando login por formulario...');
      var cookies = loginFudo_();
      if (!cookies) {
        Logger.log('❌ No se pudo autenticar en Fudo. Abortando.');
        return;
      }
      ventas = fetchSales_(cookies);
    }

    Logger.log('📦 Ventas recibidas: ' + ventas.length);
    if (ventas.length === 0) { Logger.log('Sin ventas. Fin.'); return; }

    // 2. Procesar cada venta
    var insertadas = 0, duplicadas = 0;

    ventas.forEach(function(venta) {
      var norm = normalizarVenta_(venta);

      // Saltar si no tiene ID
      if (!norm.idVentaFudo) { Logger.log('⏭ Venta sin ID, ignorada.'); return; }

      // Ya existe en Supabase → saltar
      if (!esVentaNueva_(norm.idVentaFudo)) { duplicadas++; return; }

      // Insertar en Supabase (sin user_id → el staff lo vinculará luego con QR)
      var ok = insertarEnSupabase_(norm);
      if (ok) {
        marcarVentaProcesada_(norm.idVentaFudo);
        insertadas++;
        Logger.log('✅ Insertada venta ' + norm.idVentaFudo + ' | $' + norm.monto);
      }
    });

    Logger.log('====== RESUMEN ======');
    Logger.log('Ventas leídas   : ' + ventas.length);
    Logger.log('Insertadas      : ' + insertadas);
    Logger.log('Duplicadas/skip : ' + duplicadas);
    Logger.log('=====================');

  } catch (e) {
    Logger.log('❌ ERROR GENERAL: ' + e.message);
    Logger.log(e.stack);
  }
}


// ============================================================
//  SECCIÓN 4 – AUTENTICACIÓN
// ============================================================

/**
 * Intenta obtener ventas usando el Bearer token directamente.
 * @return {Array|null}  Array de ventas o null si falló.
 */
function fetchSalesConBearer_() {
  try {
    var ahora   = new Date();
    var hace24h = new Date(ahora.getTime() - 24 * 60 * 60 * 1000);
    var desde   = Utilities.formatDate(hace24h, 'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");
    var hasta   = Utilities.formatDate(ahora,   'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");

    var url = FUDO_SALES_API_URL
            + '?from='  + encodeURIComponent(desde)
            + '&to='    + encodeURIComponent(hasta)
            + '&status=closed'
            + '&limit=500';

    var resp = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + FUDO_BEARER,
        'Accept'       : 'application/json'
      },
      muteHttpExceptions: true
    });

    var code = resp.getResponseCode();
    Logger.log('fetchSalesConBearer_ status: ' + code);

    if (code !== 200) {
      Logger.log('Bearer no funcionó (' + code + '). Respuesta: ' + resp.getContentText().substring(0, 200));
      return null;
    }

    return parsearRespuestaVentas_(resp.getContentText());

  } catch (e) {
    Logger.log('Excepción fetchSalesConBearer_: ' + e.message);
    return null;
  }
}


/**
 * Login por formulario en Fudo (fallback).
 * @return {string|null} Cookie string o null.
 */
function loginFudo_() {
  try {
    var getResp = UrlFetchApp.fetch(FUDO_LOGIN_URL, { method: 'GET', followRedirects: true, muteHttpExceptions: true });
    var getCookies = extraerCookies_(getResp.getAllHeaders());
    var html = getResp.getContentText();

    var csrfToken = '';
    var csrfMatch = html.match(/name=["\'](?:_csrf|csrf_token|_token)["\'][^>]*value=["\']([\w\-\/\+=]+)["\']/i);
    if (csrfMatch) csrfToken = csrfMatch[1];

    var payload = { 'email': FUDO_USER, 'password': FUDO_PASSWORD };
    if (csrfToken) payload['_csrf'] = csrfToken;

    var loginHeaders = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept'      : 'text/html,application/json,*/*',
      'Referer'     : FUDO_LOGIN_URL,
      'User-Agent'  : 'Mozilla/5.0 (compatible; GoogleAppsScript)'
    };
    if (getCookies) loginHeaders['Cookie'] = getCookies;

    var postResp = UrlFetchApp.fetch(FUDO_LOGIN_URL, {
      method: 'POST', payload: payload, headers: loginHeaders,
      followRedirects: true, muteHttpExceptions: true
    });

    var statusCode = postResp.getResponseCode();
    Logger.log('Login POST status: ' + statusCode);
    if (statusCode >= 400) { Logger.log('❌ Login fallido.'); return null; }

    var sessionCookies = extraerCookies_(postResp.getAllHeaders());
    return combinarCookies_(getCookies, sessionCookies) || null;

  } catch (e) {
    Logger.log('❌ Excepción loginFudo_: ' + e.message);
    return null;
  }
}


/**
 * Obtener ventas usando cookies de sesión.
 * @param  {string} cookies
 * @return {Array}
 */
function fetchSales_(cookies) {
  try {
    var ahora   = new Date();
    var hace24h = new Date(ahora.getTime() - 24 * 60 * 60 * 1000);
    var desde   = Utilities.formatDate(hace24h, 'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");
    var hasta   = Utilities.formatDate(ahora,   'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");

    var url = FUDO_SALES_API_URL
            + '?from='  + encodeURIComponent(desde)
            + '&to='    + encodeURIComponent(hasta)
            + '&status=closed&limit=500';

    var resp = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: { 'Cookie': cookies, 'Accept': 'application/json', 'Referer': 'https://app-v2.fu.do/app/' },
      followRedirects: true, muteHttpExceptions: true
    });

    var code = resp.getResponseCode();
    Logger.log('fetchSales_ status: ' + code);
    if (code !== 200) { Logger.log('Error ' + code + ': ' + resp.getContentText().substring(0, 300)); return []; }

    return parsearRespuestaVentas_(resp.getContentText());
  } catch (e) {
    Logger.log('❌ Excepción fetchSales_: ' + e.message);
    return [];
  }
}


/**
 * Parsea el body JSON de la respuesta de ventas.
 */
function parsearRespuestaVentas_(body) {
  Logger.log('📄 Primeros 600 chars: ' + body.substring(0, 600));
  try {
    var json = JSON.parse(body);
    if (Array.isArray(json))          return json;
    if (Array.isArray(json.data))     return json.data;
    if (Array.isArray(json.orders))   return json.orders;
    if (Array.isArray(json.sales))    return json.sales;
    Logger.log('⚠️ Estructura desconocida. Keys: ' + Object.keys(json).join(', '));
    return [];
  } catch (e) {
    Logger.log('❌ Error parseando JSON: ' + e.message);
    return [];
  }
}


// ============================================================
//  SECCIÓN 5 – NORMALIZAR Y CALCULAR
// ============================================================

/**
 * Normaliza una venta cruda de Fudo.
 * ⬅ Ajusta las constantes CAMPO_* si Fudo cambia el JSON.
 */
function normalizarVenta_(venta) {
  var idVentaFudo = String(venta[CAMPO_ID_VENTA] || '');
  var monto       = parseFloat(venta[CAMPO_MONTO]  || 0);
  var fecha       = venta[CAMPO_FECHA] || new Date().toISOString();

  // Datos del cliente (puede no existir)
  var customer      = venta[CAMPO_CUSTOMER] || {};
  var clienteNombre = customer[CAMPO_NOMBRE_CUSTOMER] || null;
  var clienteEmail  = customer[CAMPO_EMAIL_CUSTOMER]  || null;
  var clientePhone  = customer[CAMPO_PHONE_CUSTOMER]  || null;

  // Normalizar teléfono si existe
  if (clientePhone) clientePhone = normalizarTelefono_(String(clientePhone));

  return {
    idVentaFudo   : idVentaFudo,
    monto         : monto,
    fecha         : fecha,
    clienteNombre : clienteNombre,
    clienteEmail  : clienteEmail,
    clientePhone  : clientePhone,
    puntos        : Math.floor(monto / PESOS_POR_PUNTO)
  };
}


/**
 * Normaliza teléfono chileno a formato 56912345678 (sin +).
 */
function normalizarTelefono_(tel) {
  var limpio = tel.replace(/[^\d]/g, '');
  if (limpio.startsWith('56') && limpio.length >= 11) return limpio;
  if (limpio.startsWith('9')  && limpio.length === 9)  return '56' + limpio;
  if (limpio.length === 8)                              return '569' + limpio;
  return limpio || null;
}


// ============================================================
//  SECCIÓN 6 – INSERTAR EN SUPABASE
// ============================================================

/**
 * Inserta una venta en la tabla ventas_fudo de Supabase.
 * user_id queda NULL → el staff lo vincula luego con el QR.
 *
 * @param  {Object}  norm  Venta normalizada
 * @return {boolean}       true si OK
 */
function insertarEnSupabase_(norm) {
  try {
    var payload = JSON.stringify({
      fudo_sale_id     : norm.idVentaFudo,
      user_id          : null,                     // Sin match automático
      cliente_whatsapp : norm.clientePhone || null,
      cliente_email    : norm.clienteEmail  || null,
      cliente_nombre   : norm.clienteNombre || null,
      total_venta      : norm.monto,
      puntos_generados : norm.puntos,
      origen           : 'apps_script',
      fecha_venta      : norm.fecha
    });

    var resp = UrlFetchApp.fetch(SUPABASE_URL + '/rest/v1/ventas_fudo', {
      method     : 'POST',
      contentType: 'application/json',
      payload    : payload,
      headers    : {
        'apikey'       : SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Prefer'       : 'return=minimal'
      },
      muteHttpExceptions: true
    });

    var code = resp.getResponseCode();
    if (code === 200 || code === 201) return true;

    // 409 = ya existe (constraint UNIQUE fudo_sale_id) → ok también
    if (code === 409) { Logger.log('ℹ️ Venta ' + norm.idVentaFudo + ' ya existía en Supabase.'); return false; }

    Logger.log('⚠️ Supabase respondió ' + code + ': ' + resp.getContentText().substring(0, 200));
    return false;

  } catch (e) {
    Logger.log('❌ Excepción insertarEnSupabase_: ' + e.message);
    return false;
  }
}


// ============================================================
//  SECCIÓN 7 – ANTI-DUPLICADOS (PropertiesService)
// ============================================================

function esVentaNueva_(idVentaFudo) {
  return !PropertiesService.getScriptProperties().getProperty('PROC_' + idVentaFudo);
}

function marcarVentaProcesada_(idVentaFudo) {
  PropertiesService.getScriptProperties().setProperty('PROC_' + idVentaFudo, new Date().toISOString());
}

function limpiarVentasAntiguas() {
  var props  = PropertiesService.getScriptProperties().getProperties();
  var hoy    = new Date();
  var borradas = 0;
  Object.keys(props).forEach(function(k) {
    if (!k.startsWith('PROC_')) return;
    try {
      var dias = (hoy - new Date(props[k])) / (1000 * 60 * 60 * 24);
      if (dias > 30) { PropertiesService.getScriptProperties().deleteProperty(k); borradas++; }
    } catch (e) { PropertiesService.getScriptProperties().deleteProperty(k); borradas++; }
  });
  Logger.log('🧹 limpiarVentasAntiguas: borradas ' + borradas + ' entradas.');
}


// ============================================================
//  SECCIÓN 8 – HELPERS HTTP
// ============================================================

function extraerCookies_(headers) {
  var sc = headers['Set-Cookie'] || headers['set-cookie'];
  if (!sc) return '';
  var list = Array.isArray(sc) ? sc : [sc];
  return list.map(function(c) { return c.split(';')[0].trim(); }).filter(Boolean).join('; ');
}

function combinarCookies_(base, nuevas) {
  var mapa = {};
  function parse(s) {
    if (!s) return;
    s.split(';').forEach(function(p) {
      p = p.trim();
      var i = p.indexOf('=');
      var k = i >= 0 ? p.substring(0, i).trim() : p;
      var v = i >= 0 ? p.substring(i + 1).trim() : '';
      if (k) mapa[k] = v;
    });
  }
  parse(base); parse(nuevas);
  return Object.keys(mapa).map(function(k) { return k + '=' + mapa[k]; }).join('; ');
}


// ============================================================
//  SECCIÓN 9 – TRIGGER
// ============================================================

/**
 * Crea el trigger para ejecutar procesarVentasFudo() cada 15 min.
 * ▶ Ejecuta una sola vez.
 */
function setupTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === 'procesarVentasFudo') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('procesarVentasFudo').timeBased().everyMinutes(15).create();
  Logger.log('✅ Trigger creado: procesarVentasFudo cada 15 min.');
}


// ============================================================
//  SECCIÓN 10 – FUNCIONES DE PRUEBA
// ============================================================

/**
 * TEST PRINCIPAL: intenta autenticarse y traer ventas.
 * ▶ Ejecuta esto primero.
 */
function testFudo() {
  Logger.log('============ TEST FUDO ============');

  // Primero con Bearer
  Logger.log('--- Probando con Bearer token ---');
  var ventas = fetchSalesConBearer_();

  if (ventas !== null) {
    Logger.log('✅ Bearer token funcionó!');
    Logger.log('Ventas: ' + ventas.length);
    if (ventas.length > 0) {
      Logger.log('--- Primera venta (raw) ---');
      Logger.log(JSON.stringify(ventas[0], null, 2));
      Logger.log('--- Normalizada ---');
      Logger.log(JSON.stringify(normalizarVenta_(ventas[0]), null, 2));
    }
  } else {
    // Fallback a login por formulario
    Logger.log('--- Bearer falló, probando login por formulario ---');
    var cookies = loginFudo_();
    if (!cookies) {
      Logger.log('❌ LOGIN FALLIDO. Verifica FUDO_USER y FUDO_PASSWORD.');
      return;
    }
    Logger.log('✅ Login por formulario exitoso.');
    ventas = fetchSales_(cookies);
    Logger.log('Ventas: ' + ventas.length);
    if (ventas.length > 0) {
      Logger.log('--- Primera venta (raw) ---');
      Logger.log(JSON.stringify(ventas[0], null, 2));
    }
  }

  if (ventas.length === 0) {
    Logger.log('⚠️ Sin ventas. Corre testEndpointsAlternativos() para encontrar la URL correcta.');
  }
  Logger.log('============ FIN TEST ============');
}


/**
 * Prueba varias URLs posibles de la API de Fudo.
 * ▶ Úsalo si testFudo() no trae ventas.
 */
function testEndpointsAlternativos() {
  Logger.log('=== TEST ENDPOINTS ===');
  var urls = [
    'https://api.fu.do/v1/orders',
    'https://api.fu.do/v1/sales',
    'https://api.fu.do/orders',
    'https://app-v2.fu.do/api/v2/orders',
    'https://app-v2.fu.do/api/v2/sales',
    'https://app-v2.fu.do/api/orders',
    'https://app-v2.fu.do/api/v1/orders'
  ];

  urls.forEach(function(url) {
    try {
      var r = UrlFetchApp.fetch(url, {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + FUDO_BEARER, 'Accept': 'application/json' },
        muteHttpExceptions: true
      });
      var preview = r.getContentText().substring(0, 120).replace(/\n/g, ' ');
      Logger.log(r.getResponseCode() + ' | ' + url + ' | ' + preview);
    } catch (e) {
      Logger.log('ERR | ' + url + ' | ' + e.message);
    }
  });
  Logger.log('=== Copia la URL con status 200 a FUDO_SALES_API_URL ===');
}


/**
 * TEST: Inserta un dato directo en Supabase para verificar que la tabla existe.
 */
function testInsertarSupabase() {
  Logger.log('=== TEST SUPABASE INSERT ===');
  var ok = insertarEnSupabase_({
    idVentaFudo   : 'TEST-GAS-' + new Date().getTime(),
    monto         : 25000,
    puntos        : 2,
    fecha         : new Date().toISOString(),
    clienteNombre : 'Prueba Apps Script',
    clienteEmail  : null,
    clientePhone  : null
  });
  Logger.log(ok ? '✅ Inserción exitosa en Supabase!' : '❌ Falló la inserción. Revisa los logs.');
}


/**
 * Muestra las ventas procesadas en PropertiesService.
 */
function verVentasProcesadas() {
  var props  = PropertiesService.getScriptProperties().getProperties();
  var claves = Object.keys(props).filter(function(k) { return k.startsWith('PROC_'); });
  Logger.log('Ventas procesadas: ' + claves.length);
  claves.slice(0, 20).forEach(function(k) { Logger.log(k + ' → ' + props[k]); });
}
