<template>
  <v-dialog :model-value="modelValue" @update:model-value="cancel" persistent max-width="500px">
    <v-card>
      <v-card-title class="text-h5">{{ title }}</v-card-title>
      <v-card-text>{{ text }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="cancel">Отмена</v-btn>
        <v-btn color="primary" variant="flat" @click="confirm">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

const cancel = () => {
  emit('cancel');
  emit('update:modelValue', false);
};

const confirm = () => {
  emit('confirm');
  emit('update:modelValue', false);
};
</script>
