<!-- frontend/src/components/layouts/MainLayout.vue -->
<template>
    <v-app-bar app color="primary">
        <v-app-bar-title>Зелёный Рейнджер</v-app-bar-title>
    </v-app-bar>
    <v-main>
        <v-container>
        <router-view />
        </v-container>
    </v-main>
</template>
