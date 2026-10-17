<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter, useRoute, RouterLink } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo & Liens de navigation -->
        <div class="flex items-center space-x-8">
          <div class="flex-shrink-0 flex items-center">
            <span class="text-xl font-bold tracking-tight text-gray-900">Hongre</span>
            <span class="ml-2 text-xs font-semibold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800">Trésorerie</span>
          </div>
          <div class="hidden sm:flex sm:space-x-6">
            <RouterLink to="/" 
                        :class="[route.path === '/' 
                          ? 'border-indigo-600 text-indigo-600' 
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 
                          'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors']">
              Tableau de bord
            </RouterLink>
            <RouterLink to="/operations" 
                        :class="[route.path === '/operations' 
                          ? 'border-indigo-600 text-indigo-600' 
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 
                          'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors']">
              Opérations
            </RouterLink>
          </div>
        </div>

        <!-- Profil & Déconnexion -->
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-600 font-medium" v-if="authStore.user">
            {{ authStore.user.nom }}
          </span>
          <button @click="handleLogout" 
                  class="text-sm font-medium text-gray-500 hover:text-red-600 transition-colors">
            Déconnexion
          </button>
        </div>
      </div>
    </div>

    <!-- Menu mobile -->
    <div class="sm:hidden border-t border-gray-100 px-4 py-2 flex space-x-6 bg-gray-50">
      <RouterLink to="/" 
                  :class="[route.path === '/' ? 'text-indigo-600 font-semibold' : 'text-gray-600 font-medium', 'text-sm']">
        Tableau de bord
      </RouterLink>
      <RouterLink to="/operations" 
                  :class="[route.path === '/operations' ? 'text-indigo-600 font-semibold' : 'text-gray-600 font-medium', 'text-sm']">
        Opérations
      </RouterLink>
    </div>
  </nav>
</template>
