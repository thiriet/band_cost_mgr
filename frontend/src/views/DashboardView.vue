<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';
import AppNavbar from '../components/AppNavbar.vue';

const authStore = useAuthStore();
const router = useRouter();

const balances = ref(null);
const loading = ref(true);
const error = ref(false);

// État de la modale de remboursement / régularisation
const showModal = ref(false);
const modalType = ref('REMBOURSEMENT'); // 'REMBOURSEMENT' (Caisse -> Créancier) ou 'REGULARISATION' (Débiteur -> Caisse)
const selectedMemberId = ref('');
const amount = ref('');
const dateTransaction = ref(new Date().toISOString().split('T')[0]);
const details = ref('');
const isSubmitting = ref(false);
const formError = ref('');

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

const caisseDisponible = computed(() => {
  return Number(balances.value?.caisse_commune || 0);
});

const crediteurs = computed(() => {
  return (balances.value?.membres || []).filter(m => Number(m.solde) > 0);
});

const debiteurs = computed(() => {
  return (balances.value?.membres || []).filter(m => Number(m.solde) < 0);
});

const selectedMember = computed(() => {
  if (!selectedMemberId.value || !balances.value) return null;
  return balances.value.membres.find(m => m.id_membre === Number(selectedMemberId.value));
});

const openModal = () => {
  formError.value = '';
  modalType.value = caisseDisponible.value > 0 && crediteurs.value.length > 0 ? 'REMBOURSEMENT' : 'REGULARISATION';
  selectedMemberId.value = modalType.value === 'REMBOURSEMENT' 
    ? (crediteurs.value[0]?.id_membre || '') 
    : (debiteurs.value[0]?.id_membre || '');
  amount.value = '';
  details.value = '';
  dateTransaction.value = new Date().toISOString().split('T')[0];
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const setMaxAmount = () => {
  if (!selectedMember.value) return;
  const soldeAbs = Math.abs(Number(selectedMember.value.solde));
  if (modalType.value === 'REMBOURSEMENT') {
    amount.value = Math.min(caisseDisponible.value, soldeAbs).toFixed(2);
  } else {
    amount.value = soldeAbs.toFixed(2);
  }
};

const handleSubmit = async () => {
  formError.value = '';
  const parsedAmount = parseFloat(amount.value);

  if (isNaN(parsedAmount) || parsedAmount <= 0) {
    formError.value = "Veuillez saisir un montant strictement positif.";
    return;
  }

  if (!selectedMemberId.value) {
    formError.value = "Veuillez sélectionner un musicien.";
    return;
  }

  if (modalType.value === 'REMBOURSEMENT') {
    if (parsedAmount > caisseDisponible.value) {
      formError.value = `Le montant ne peut pas dépasser la trésorerie disponible (${caisseDisponible.value.toFixed(2)} €).`;
      return;
    }
  }

  isSubmitting.value = true;
  try {
    if (modalType.value === 'REMBOURSEMENT') {
      await api.post('/transactions/', {
        type_transaction: 'REMBOURSEMENT',
        categorie: 'Remboursement',
        details: details.value || `Remboursement de ${selectedMember.value.nom}`,
        montant: parsedAmount,
        date_transaction: dateTransaction.value,
        id_payeur: null, // Caisse Commune
        participants: [Number(selectedMemberId.value)],
        source: 'WEB'
      });
    } else {
      // Régularisation d'une dette vers la Caisse Commune
      await api.post('/transactions/', {
        type_transaction: 'REVENU',
        categorie: 'Régularisation',
        details: details.value || `Règlement de dette par ${selectedMember.value.nom}`,
        montant: parsedAmount,
        date_transaction: dateTransaction.value,
        id_payeur: null,
        participants: [],
        source: 'WEB'
      });
    }

    closeModal();
    await fetchBalances();
  } catch (err) {
    console.error("Erreur enregistrement opération", err);
    formError.value = err.response?.data?.detail || "Une erreur est survenue lors de l'enregistrement.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <AppNavbar />

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      
      <!-- En-tête avec bouton d'action -->
      <div class="flex justify-between items-center mb-6 px-4 sm:px-0">
        <h2 class="text-2xl font-bold text-gray-900">Tableau de bord</h2>
        <button class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shadow-sm text-sm font-medium transition-colors"
                @click="openModal">
          + Saisir un Remboursement / Virement
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
                  Number(membre.solde) > 0 ? 'bg-green-100 text-green-800' : 
                  Number(membre.solde) < 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800',
                  'px-2.5 py-0.5 rounded-full text-sm font-medium'
                ]">
                  {{ Number(membre.solde) > 0 ? '+' : '' }}{{ membre.solde }} €
                </span>
              </div>
              <p class="mt-2 text-sm text-gray-500">
                <span v-if="Number(membre.solde) < 0">Doit verser à la caisse</span>
                <span v-else-if="Number(membre.solde) > 0">La caisse lui doit</span>
                <span v-else>À l'équilibre</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modale de Saisie Remboursement / Régularisation -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-lg w-full p-6 shadow-xl relative">
        <h3 class="text-lg font-bold text-gray-900 mb-4">
          Saisir une régularisation
        </h3>

        <!-- Toggle Type d'opération -->
        <div class="flex bg-gray-100 p-1 rounded-lg mb-4 text-xs font-medium">
          <button type="button"
                  @click="modalType = 'REMBOURSEMENT'; selectedMemberId = crediteurs[0]?.id_membre || ''"
                  :class="[modalType === 'REMBOURSEMENT' ? 'bg-white shadow text-indigo-600 font-bold' : 'text-gray-600', 'flex-1 py-2 rounded-md transition-all']">
            La Caisse rembourse un créancier
          </button>
          <button type="button"
                  @click="modalType = 'REGULARISATION'; selectedMemberId = debiteurs[0]?.id_membre || ''"
                  :class="[modalType === 'REGULARISATION' ? 'bg-white shadow text-indigo-600 font-bold' : 'text-gray-600', 'flex-1 py-2 rounded-md transition-all']">
            Un membre verse à la Caisse
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Avertissement si Caisse vide pour un remboursement -->
          <div v-if="modalType === 'REMBOURSEMENT' && caisseDisponible <= 0" class="p-3 bg-amber-50 border-l-4 border-amber-400 text-xs text-amber-800">
            ⚠️ La caisse ne dispose actuellement d'aucun fonds (0,00 €). Un remboursement ne peut être effectué que si la caisse a de la trésorerie.
          </div>

          <!-- Sélection du membre -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              {{ modalType === 'REMBOURSEMENT' ? 'Musicien à rembourser (créancier) :' : 'Musicien qui régularise (débiteur) :' }}
            </label>
            <select v-model="selectedMemberId" required class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500">
              <template v-if="modalType === 'REMBOURSEMENT'">
                <option v-for="m in crediteurs" :key="m.id_membre" :value="m.id_membre">
                  {{ m.nom }} (créance : +{{ m.solde }} €)
                </option>
                <option v-if="crediteurs.length === 0" disabled value="">Aucun membre créancier</option>
              </template>
              <template v-else>
                <option v-for="m in debiteurs" :key="m.id_membre" :value="m.id_membre">
                  {{ m.nom }} (dette : {{ m.solde }} €)
                </option>
                <option v-if="debiteurs.length === 0" disabled value="">Aucun membre débiteur</option>
              </template>
            </select>
          </div>

          <!-- Montant -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="block text-xs font-semibold text-gray-700">Montant (€) :</label>
              <button v-if="selectedMember" type="button" @click="setMaxAmount" class="text-xs text-indigo-600 hover:text-indigo-800 underline">
                Remplir au maximum
              </button>
            </div>
            <input type="number" step="0.01" min="0.01" v-model="amount" required placeholder="0.00"
                   class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500" />
            <p v-if="modalType === 'REMBOURSEMENT'" class="text-xs text-gray-500 mt-1">
              Trésorerie disponible en caisse : <b>{{ caisseDisponible.toFixed(2) }} €</b>
            </p>
          </div>

          <!-- Date -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">Date de l'opération :</label>
            <input type="date" v-model="dateTransaction" required
                   class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500" />
          </div>

          <!-- Détails -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">Détails / Note (optionnel) :</label>
            <input type="text" v-model="details" placeholder="ex: Virement bancaire, cash..."
                   class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500" />
          </div>

          <!-- Message d'erreur -->
          <div v-if="formError" class="text-xs text-red-600 bg-red-50 p-2 rounded">
            {{ formError }}
          </div>

          <!-- Boutons -->
          <div class="flex justify-end space-x-3 pt-3 border-t">
            <button type="button" @click="closeModal" class="px-4 py-2 border rounded-md text-sm text-gray-700 hover:bg-gray-50">
              Annuler
            </button>
            <button type="submit" :disabled="isSubmitting || (modalType === 'REMBOURSEMENT' && caisseDisponible <= 0)"
                    class="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors">
              {{ isSubmitting ? 'Enregistrement...' : 'Confirmer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
