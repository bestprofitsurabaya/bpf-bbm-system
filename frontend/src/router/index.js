import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore, ROLE_META } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/403', name: 'forbidden', component: () => import('../views/ForbiddenView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/AppLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('../views/HomeView.vue') },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/dashboard/AdminDashboard.vue'), meta: { roles: ['admin', 'ga', 'finance'] } },
      { path: 'marketing', name: 'marketing', component: () => import('../views/dashboard/MarketingDashboard.vue'), meta: { roles: ['marketing'] } },
      { path: 'chief-driver', name: 'chief-driver', component: () => import('../views/dashboard/ChiefDriverDashboard.vue'), meta: { roles: ['chief_driver', 'ga', 'admin'] } },
      { path: 'trips', name: 'trips', component: () => import('../views/TripsView.vue'), meta: { roles: ['ga', 'finance', 'admin'] } },
      { path: 'assignments', name: 'assignments', component: () => import('../views/AssignmentsView.vue'), meta: { roles: ['ga', 'admin'] } },
      { path: 'rekap', name: 'rekap', component: () => import('../views/RekapView.vue'), meta: { roles: ['finance', 'admin'] } },
      { path: 'cash', name: 'cash', component: () => import('../views/CashView.vue'), meta: { roles: ['ga', 'finance', 'admin'] } },
      { path: 'analytics', name: 'analytics', component: () => import('../views/AnalyticsView.vue'), meta: { roles: ['ga', 'finance', 'admin'] } },
      { path: 'users', name: 'users', component: () => import('../views/UsersView.vue'), meta: { roles: ['admin'] } },
      { path: 'settings', name: 'settings', component: () => import('../views/SettingsView.vue'), meta: { roles: ['admin'] } },
      { path: 'logs', name: 'logs', component: () => import('../views/LogsView.vue'), meta: { roles: ['admin'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHistory('/app/'),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) await auth.bootstrap()

  if (to.meta.public) {
    if (to.name === 'login' && auth.isAuthenticated) {
      return ROLE_META[auth.role] ? { path: ROLE_META[auth.role].home } : true
    }
    return true
  }

  if (!auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }
  const roles = to.meta.roles
  if (roles && !roles.includes(auth.role)) {
    return { name: 'forbidden' }
  }
  return true
})

export default router
