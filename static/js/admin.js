/* ============================================================ */
/* BPF FLEET SYSTEM - Admin Dashboard Bootstrap                  */
/*                                                               */
/* Split into:                                                   */
/*   admin-ui.js         - toast, dialogs, PIN session cache     */
/*   admin-dashboard.js  - workflow, cross-check, review, socket */
/*   admin-cash.js       - kasbon (cash request)                 */
/*   admin.js            - this bootstrap (init only)            */
/* ============================================================ */

if (document.getElementById('dailyCodeInput')) loadDailyCode();
if (document.getElementById('cashRequestList')) loadCashRequests();
setupSocket();
