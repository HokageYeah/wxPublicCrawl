<template>
  <div class="min-h-screen flex flex-col">
    <header class="p-4 border-b border-gray-800">
      <div class="container mx-auto flex items-center justify-between">
        <h1 class="text-xl font-bold">WeChat QR Code Login</h1>
      </div>
    </header>
    
    <main class="flex-1 container mx-auto p-4">
      <RouterView />
    </main>
    
    <footer class="p-4 border-t border-gray-800 text-center text-gray-500 text-sm">
      &copy; {{ new Date().getFullYear() }} WeChat QR Code Login Demo
    </footer>
  </div>
</template>

<script setup lang="ts">

</script> 