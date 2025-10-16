<template>
  <div class="min-h-screen bg-white">
    <!-- Nav -->
    <header class="sticky top-0 z-20 backdrop-blur bg-white/80 border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center shadow-sm">
            <Icon name="heroicons:chat-bubble-left-right" class="h-5 w-5 text-white" />
          </div>
          <span class="font-semibold text-gray-900">AL‑Tech Academy</span>
        </div>
        <div class="flex items-center gap-3">
          <button @click="navigateTo('/auth')" class="px-4 py-2 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition">Sign up / Sign in</button>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-emerald-50"></div>
      <div class="relative max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight text-gray-900">AI‑powered academic help for students, experts, and admins</h1>
          <p class="mt-4 text-lg text-gray-600">Beautifully simple, Apple‑inspired experience with trustworthy assistance. Ask questions, review answers, and manage the system from one place.</p>
          <div class="mt-8 flex items-center gap-3">
            <button @click="navigateTo('/auth')" class="px-5 py-3 rounded-xl bg-emerald-500 text-white hover:bg-emerald-600 shadow-sm">Get started</button>
            <button @click="scrollTo('#features')" class="px-5 py-3 rounded-xl bg-white text-emerald-700 border border-emerald-200 hover:bg-emerald-50">Learn more</button>
          </div>
        </div>
        <div class="md:pl-10">
          <div class="rounded-2xl border border-emerald-100 bg-white shadow-sm p-6">
            <div class="grid grid-cols-3 gap-4 text-center">
              <div>
                <div class="text-3xl font-bold text-gray-900">24/7</div>
                <div class="text-sm text-gray-500">Availability</div>
              </div>
              <div>
                <div class="text-3xl font-bold text-gray-900">99.9%</div>
                <div class="text-sm text-gray-500">Uptime</div>
              </div>
              <div>
                <div class="text-3xl font-bold text-gray-900">A+</div>
                <div class="text-sm text-gray-500">Quality</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="max-w-7xl mx-auto px-6 py-16">
      <h2 class="text-2xl md:text-3xl font-bold text-gray-900 text-center">What we offer</h2>
      <p class="mt-3 text-gray-600 text-center max-w-2xl mx-auto">A focused suite of tools that help students learn, experts review, and admins manage — all in a clean, minimal interface.</p>
      <div class="mt-10 grid md:grid-cols-3 gap-6">
        <div class="rounded-2xl border border-gray-100 p-6 hover:shadow-sm transition">
          <div class="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
            <Icon name="heroicons:academic-cap" class="h-6 w-6" />
          </div>
          <h3 class="font-semibold text-gray-900">Student Q&A</h3>
          <p class="mt-2 text-gray-600">Ask academic questions and receive clear, structured answers powered by AI.</p>
        </div>
        <div class="rounded-2xl border border-gray-100 p-6 hover:shadow-sm transition">
          <div class="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
            <Icon name="heroicons:adjustments-horizontal" class="h-6 w-6" />
          </div>
          <h3 class="font-semibold text-gray-900">Expert Review</h3>
          <p class="mt-2 text-gray-600">Experts refine AI responses to ensure accuracy, clarity, and academic integrity.</p>
        </div>
        <div class="rounded-2xl border border-gray-100 p-6 hover:shadow-sm transition">
          <div class="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
            <Icon name="heroicons:shield-check" class="h-6 w-6" />
          </div>
          <h3 class="font-semibold text-gray-900">Admin Controls</h3>
          <p class="mt-2 text-gray-600">Monitor performance, manage roles, and maintain system health with ease.</p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="relative">
      <div class="absolute inset-0 bg-emerald-50"></div>
      <div class="relative max-w-7xl mx-auto px-6 py-16 text-center">
        <h3 class="text-2xl font-bold text-gray-900">Ready to get started?</h3>
        <p class="mt-2 text-gray-600">Create an account as a Student or Expert, or sign in as Admin.</p>
        <button @click="navigateTo('/auth')" class="mt-6 px-6 py-3 rounded-xl bg-emerald-500 text-white hover:bg-emerald-600 shadow-sm">Sign up / Sign in</button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { navigateTo } from '#app'

const scrollTo = (selector: string) => {
  const el = document.querySelector(selector)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>