<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';

const authStore = useAuthStore();
const router = useRouter();

const balances = ref(null);
const loading = ref(true);
const error = ref(false);

const fetchBalances = async () => {
  error.value = false;
  loading.value = true;
  try {
    const response = await api.get('/transactions/balances');
    balances.value = response.data;
  } catch (err) {
    console.error("Erreur lors de la récupération des soldes", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchBalances();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Hongre - Trésorerie</h1>
          </div>
          <div class="flex items-center">
            <span class="mr-4 text-sm text-gray-600" v-if="authStore.user">Connecté en tant que {{ authStore.user.nom }}</span>
            <button @click="handleLogout" class="text-sm text-red-600 hover:text-red-800">Déconnexion</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      
      <!-- En-tête avec bouton d'action -->
      <div class="flex justify-between items-center mb-6 px-4 sm:px-0">
        <h2 class="text-2xl font-bold text-gray-900">Tableau de bord</h2>
        <button class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shadow-sm text-sm font-medium"
                onclick="alert('La modale de saisie de Remboursement sera développée prochainement !')">
          + Saisir un Remboursement
        </button>
      </div>

      <div v-if="loading" class="text-center py-10 text-gray-500">
        <svg class="animate-spin h-8 w-8 mx-auto mb-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Chargement des soldes...
      </div>

      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 mx-4 sm:mx-0">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">
              Impossible de récupérer les données depuis le serveur.
            </p>
            <p class="mt-2 text-sm md:mt-0 md:ml-6">
              <button @click="fetchBalances" class="whitespace-nowrap font-medium text-red-700 hover:text-red-600 underline">Réessayer</button>
            </p>
          </div>
        </div>
      </div>
      
      <div v-else-if="balances">
        <!-- Caisse Commune -->
        <div class="bg-white overflow-hidden shadow rounded-lg mb-6">
          <div class="px-4 py-5 sm:p-6 text-center">
            <h3 class="text-lg leading-6 font-medium text-gray-900">Solde de la Caisse Commune</h3>
            <div class="mt-2 text-4xl font-extrabold text-indigo-600">
              {{ balances.caisse_commune }} €
            </div>
            <p class="mt-1 text-sm text-gray-500">Montant total disponible dans le pot commun.</p>
          </div>
        </div>

        <!-- Soldes individuels -->
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4 px-4 sm:px-0">Soldes individuels</h3>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="membre in balances.membres" :key="membre.id_membre" class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex justify-between items-center">
                <h4 class="text-md font-medium text-gray-900">{{ membre.nom }}</h4>
                <span :class="[
                  membre.solde > 0 ? 'bg-green-100 text-green-800' : 
                  membre.solde < 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800',
                  'px-2.5 py-0.5 rounded-full text-sm font-medium'
                ]">
                  {{ membre.solde > 0 ? '+' : '' }}{{ membre.solde }} €
                </span>
              </div>
              <p class="mt-2 text-sm text-gray-500">
                <span v-if="membre.solde < 0">Doit verser à la caisse</span>
                <span v-else-if="membre.solde > 0">La caisse lui doit</span>
                <span v-else>À l'équilibre</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
