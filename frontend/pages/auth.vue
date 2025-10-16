<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
    <div class="w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6 text-center">Create an account or Sign in</h1>

      <!-- Role selector -->
      <div class="flex justify-center gap-3 mb-8">
        <button
          class="px-4 py-2 rounded-lg border"
          :class="role === 'client' ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'"
          @click="role = 'client'"
        >Student</button>
        <button
          class="px-4 py-2 rounded-lg border"
          :class="role === 'expert' ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'"
          @click="role = 'expert'"
        >Expert</button>
        <button
          class="px-4 py-2 rounded-lg border"
          :class="role === 'admin' ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'"
          @click="role = 'admin'"
        >Admin</button>
      </div>

      <!-- Tabs -->
      <div class="flex justify-center gap-4 mb-6">
        <button
          class="px-3 py-1 rounded-md"
          :class="mode === 'signup' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'"
          @click="mode = 'signup'"
        >Sign up</button>
        <button
          class="px-3 py-1 rounded-md"
          :class="mode === 'signin' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'"
          @click="mode = 'signin'"
        >Sign in</button>
      </div>

      <!-- Forms -->
      <form @submit.prevent="handleSubmit" class="space-y-4 max-w-xl mx-auto">
        <div v-if="mode === 'signup'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">First name</label>
            <input v-model="firstName" type="text" class="input-primary w-full" required />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Last name</label>
            <input v-model="lastName" type="text" class="input-primary w-full" required />
          </div>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Email</label>
          <input v-model="email" type="email" class="input-primary w-full" required />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Password</label>
          <input v-model="password" type="password" class="input-primary w-full" required />
        </div>

        <button type="submit" class="btn-primary w-full mt-2">
          {{ mode === 'signup' ? actionLabel : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const role = ref<'client' | 'expert' | 'admin'>('client')
const mode = ref<'signup' | 'signin'>('signup')

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')

const actionLabel = computed(() => {
  if (role.value === 'client') return 'Create student account'
  if (role.value === 'expert') return 'Apply as expert'
  return 'Admin account (manual only)'
})

const handleSubmit = async () => {
  try {
    if (mode.value === 'signup') {
      if (role.value === 'admin') {
        // Admin signup is manual-only; allow direct sign-in if credentials exist
        await auth.login(email.value, password.value)
      } else {
        const name = `${firstName.value} ${lastName.value}`.trim()
        // @ts-ignore: Role string accepted by store
        await auth.register(email.value, password.value, name, role.value)
      }
    } else {
      await auth.login(email.value, password.value)
    }
    router.push('/')
  } catch (e) {
    console.error(e)
    alert('Authentication failed. Please check your details and try again.')
  }
}
</script>

<style scoped>
/* Tailwind utility classes are used; no custom styles */
</style>


