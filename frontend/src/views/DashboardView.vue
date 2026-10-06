<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';

const authStore = useAuthStore();
const router = useRouter();

const balances = ref(null);
const loading = ref(true);

const fetchBalances = async () => {
  try {
    const response = await api.get('/transactions/balances');
    balances.value = response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des soldes", error);
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
      <div v-if="loading" class="text-center py-10">
        Chargement...
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
