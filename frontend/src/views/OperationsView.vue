<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import AppNavbar from '../components/AppNavbar.vue';

const transactions = ref([]);
const loading = ref(true);
const error = ref(false);
const activeFilter = ref('ALL'); // ALL, DEPENSE, REVENU, REMBOURSEMENT

const fetchTransactions = async () => {
  error.value = false;
  loading.value = true;
  try {
    const response = await api.get('/transactions/');
    transactions.value = response.data;
  } catch (err) {
    console.error("Erreur lors de la récupération des transactions", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchTransactions();
});

const filteredTransactions = computed(() => {
  if (activeFilter.value === 'ALL') return transactions.value;
  return transactions.value.filter(t => t.type_transaction === activeFilter.value);
});

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  return `${day}/${month}/${year}`;
};

const formatParticipants = (participants) => {
  if (!participants || participants.length === 0) return '—';
  if (participants.length === 4) return 'Tout le groupe (4)';
  return participants.join(', ');
};

const handleDelete = async (id, details) => {
  const confirmation = window.confirm(
    `Êtes-vous sûr de vouloir supprimer l'opération "${details || 'Sans titre'}" ?\n\nCette action recalculera immédiatement tous les soldes.`
  );
  if (!confirmation) return;

  try {
    await api.delete(`/transactions/${id}`);
    await fetchTransactions();
  } catch (err) {
    console.error("Erreur suppression transaction", err);
    alert("Impossible de supprimer cette transaction.");
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <AppNavbar />

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- En-tête -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 px-4 sm:px-0 gap-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Historique des opérations</h2>
          <p class="text-sm text-gray-500 mt-1">Toutes les dépenses, revenus et remboursements du groupe</p>
        </div>

        <!-- Filtres rapides -->
        <div class="flex bg-white rounded-lg p-1 shadow-sm border border-gray-200">
          <button @click="activeFilter = 'ALL'"
                  :class="[activeFilter === 'ALL' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900', 'px-3 py-1.5 rounded-md text-xs font-medium transition-colors']">
            Toutes ({{ transactions.length }})
          </button>
          <button @click="activeFilter = 'DEPENSE'"
                  :class="[activeFilter === 'DEPENSE' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900', 'px-3 py-1.5 rounded-md text-xs font-medium transition-colors']">
            Dépenses
          </button>
          <button @click="activeFilter = 'REVENU'"
                  :class="[activeFilter === 'REVENU' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900', 'px-3 py-1.5 rounded-md text-xs font-medium transition-colors']">
            Revenus
          </button>
          <button @click="activeFilter = 'REMBOURSEMENT'"
                  :class="[activeFilter === 'REMBOURSEMENT' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900', 'px-3 py-1.5 rounded-md text-xs font-medium transition-colors']">
            Remboursements
          </button>
        </div>
      </div>

      <!-- État de chargement -->
      <div v-if="loading" class="text-center py-12 text-gray-500">
        <svg class="animate-spin h-8 w-8 mx-auto mb-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Chargement des opérations...
      </div>

      <!-- Erreur -->
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 mx-4 sm:mx-0">
        <div class="flex justify-between items-center">
          <p class="text-sm text-red-700">Impossible de charger les opérations.</p>
          <button @click="fetchTransactions" class="text-sm font-medium text-red-700 underline">Réessayer</button>
        </div>
      </div>

      <!-- Tableau des opérations -->
      <div v-else class="bg-white shadow overflow-hidden rounded-lg mx-4 sm:mx-0">
        <div v-if="filteredTransactions.length === 0" class="text-center py-12 text-gray-500 text-sm">
          Aucune opération trouvée pour ce filtre.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 text-left text-sm">
            <thead class="bg-gray-50 text-gray-500 uppercase tracking-wider text-xs">
              <tr>
                <th scope="col" class="px-6 py-3 font-medium">Date</th>
                <th scope="col" class="px-6 py-3 font-medium">Description</th>
                <th scope="col" class="px-6 py-3 font-medium">Type</th>
                <th scope="col" class="px-6 py-3 font-medium">Payé par</th>
                <th scope="col" class="px-6 py-3 font-medium">Pour</th>
                <th scope="col" class="px-6 py-3 font-medium text-right">Montant</th>
                <th scope="col" class="px-6 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="t in filteredTransactions" :key="t.id" class="hover:bg-gray-50 transition-colors">
                <!-- Date -->
                <td class="px-6 py-4 whitespace-nowrap text-gray-500 font-mono text-xs">
                  {{ formatDate(t.date_transaction) }}
                </td>

                <!-- Description & Catégorie -->
                <td class="px-6 py-4">
                  <div class="font-medium text-gray-900">{{ t.details || '—' }}</div>
                  <span class="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                    {{ t.categorie }}
                  </span>
                </td>

                <!-- Type -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="t.type_transaction === 'REVENU'"
                        class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                    Revenu
                  </span>
                  <span v-else-if="t.type_transaction === 'REMBOURSEMENT'"
                        class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                    Remboursement
                  </span>
                  <span v-else
                        class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                    Dépense
                  </span>
                </td>

                <!-- Payé par -->
                <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-800">
                  {{ t.nom_payeur }}
                </td>

                <!-- Pour -->
                <td class="px-6 py-4 text-gray-600">
                  {{ formatParticipants(t.participants_noms) }}
                </td>

                <!-- Montant -->
                <td class="px-6 py-4 whitespace-nowrap text-right font-bold text-base font-mono">
                  <span :class="t.type_transaction === 'REVENU' ? 'text-green-600' : 'text-gray-900'">
                    {{ t.type_transaction === 'REVENU' ? '+' : '' }}{{ t.montant }} €
                  </span>
                </td>

                <!-- Suppression -->
                <td class="px-6 py-4 whitespace-nowrap text-right text-xs">
                  <button @click="handleDelete(t.id, t.details)"
                          title="Supprimer cette opération"
                          class="text-gray-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>
