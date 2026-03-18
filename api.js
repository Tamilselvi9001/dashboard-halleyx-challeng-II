/* ═══════════════════════════════════════════════════
   api.js  —  NexDash Frontend API Helper
   Include this in every HTML file:
   <script src="api.js"></script>

   All functions return Promises.
   Usage example:
     API.orders.getAll().then(function(orders){ ... })
     API.orders.create(data).then(function(order){ ... })
═══════════════════════════════════════════════════ */

var API_BASE = 'http://localhost:8000';

var API = {

  /* ─────────────────────────────
     INTERNAL FETCH HELPER
  ───────────────────────────── */
  _fetch: function(method, path, body) {
    var options = {
      method:  method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);
    return fetch(API_BASE + path, options)
      .then(function(res) {
        if (!res.ok) {
          return res.json().then(function(err) {
            throw new Error(err.detail || 'API Error ' + res.status);
          });
        }
        return res.json();
      });
  },

  /* ─────────────────────────────
     ORDERS
  ───────────────────────────── */
  orders: {

    /* GET /orders → returns array of orders */
    getAll: function() {
      return API._fetch('GET', '/orders');
    },

    /* POST /orders → creates order, returns new order */
    create: function(data) {
      return API._fetch('POST', '/orders', data);
    },

    /* PUT /orders/:id → updates order, returns updated order */
    update: function(id, data) {
      return API._fetch('PUT', '/orders/' + id, data);
    },

    /* DELETE /orders/:id → deletes order */
    remove: function(id) {
      return API._fetch('DELETE', '/orders/' + id);
    }
  },

  /* ─────────────────────────────
     DASHBOARD
  ───────────────────────────── */
  dashboard: {

    /* GET /dashboard → returns { configured, widgets[] } */
    get: function() {
      return API._fetch('GET', '/dashboard');
    },

    /* POST /dashboard → saves all widgets at once */
    save: function(widgets) {
      /* Convert canvas widget objects to API format */
      var payload = widgets.map(function(w) {
        /* Pull out known top-level fields, rest goes into config_json */
        var known = ['id','type','wtype','title','x','y','cardW','configured'];
        var config = {};
        Object.keys(w).forEach(function(k) {
          if (known.indexOf(k) === -1) config[k] = w[k];
        });
        return {
          id:          w.id,
          type:        w.type        || '',
          wtype:       w.wtype       || '',
          title:       w.title       || 'Untitled',
          x:           w.x           || 0,
          y:           w.y           || 0,
          card_w:      w.cardW       || 300,
          configured:  w.configured  || false,
          config_json: config
        };
      });
      return API._fetch('POST', '/dashboard', { widgets: payload });
    },

    /* DELETE /dashboard/:id → deletes one widget */
    removeWidget: function(id) {
      return API._fetch('DELETE', '/dashboard/' + id);
    }
  }
};

/* ─────────────────────────────
   UTILITY: Show error toast
   Call this if an API call fails
───────────────────────────── */
function apiError(err) {
  console.error('API Error:', err);
  var msg = err.message || 'Something went wrong. Is the server running?';
  if (typeof showToast === 'function') showToast('Error: ' + msg);
  else alert('Error: ' + msg);
}
