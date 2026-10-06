import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email, password) {
      try {
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 expects 'username'
        formData.append('password', password);
        
        const response = await api.post('/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        this.token = response.data.access_token;
        localStorage.setItem('token', this.token);
        
        await this.fetchUser();
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    async fetchUser() {
      if (!this.token) return;
      try {
        const response = await api.get('/auth/me');
        this.user = response.data;
      } catch (error) {
        this.logout();
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
    }
  }
});
