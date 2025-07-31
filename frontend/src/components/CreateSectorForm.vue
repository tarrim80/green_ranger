<template>
  <v-form ref="form">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formData.name"
            label="Название участка"
            :rules="[requiredRule]"
            required
          ></v-text-field>
        </v-col>

        <v-col cols="12" v-if="props.showCuratorSelection">
          <v-select
            v-model="formData.curator_id"
            :items="props.curators"
            item-title="fullname"
            item-value="id"
            label="Куратор"
            :rules="[requiredRule]"
            required
          ></v-select>
        </v-col>

        <v-col cols="12" v-if="props.showCuratorSelection">
          <v-checkbox
            v-model="assignTeam"
            label="Назначить команду"
          ></v-checkbox>
        </v-col>

        <v-col cols="12" v-if="assignTeam">
          <v-select
            v-model="formData.team_id"
            :items="props.teams"
            item-title="name"
            item-value="id"
            label="Команда"
            :rules="assignTeam ? [requiredRule] : []"
            required
          ></v-select>
        </v-col>
        
        <v-col cols="12">
          <p class="text-subtitle-1">Цвет участка</p>
          <v-color-picker
            v-model="formData.color"
            mode="hex"
            hide-alpha
          ></v-color-picker>
        </v-col>
      </v-row>
    </v-container>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="cancel">Отмена</v-btn>
      <v-btn color="primary" variant="flat" @click="saveSector">Сохранить</v-btn>
    </v-card-actions>
  </v-form>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUiStore } from '@/stores/uiStore';

const props = defineProps({
  curators: { type: Array, required: true },
  teams: { type: Array, default: () => [] },
  geometry: { type: Object, default: null },
  showCuratorSelection: { type: Boolean, default: true },
  preselectedCuratorId: { type: Number, default: null },
  sectorData: { type: Object, default: null },
  initialColor: { type: String, default: '#1DE9B6' },
});

const emit = defineEmits(['save']);
const uiStore = useUiStore();

const form = ref(null);
const assignTeam = ref(false);
const formData = ref({
  name: '',
  color: '#1DE9B6',
  curator_id: null,
  team_id: null,
});

const requiredRule = (v) => !!v || 'Поле обязательно для заполнения';

onMounted(() => {
  if (props.sectorData) {
    formData.value.name = props.sectorData.name;
    formData.value.color = props.sectorData.color;
    formData.value.curator_id = props.sectorData.curator_id;
    formData.value.team_id = props.sectorData.team_id;
    if (props.sectorData.team_id) {
      assignTeam.value = true;
    }
  } else {
    formData.value.color = props.initialColor;
  }

  if (!props.showCuratorSelection) {
    formData.value.curator_id = props.preselectedCuratorId;
  }
});

const cancel = () => {
  uiStore.closePanel();
};

const saveSector = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;
  
  const payload = { ...formData.value };
  
  if (props.sectorData?.id) {
    payload.id = props.sectorData.id;
  }
  
  if (props.geometry) {
    payload.geometry = props.geometry;
  }
  
  if (!assignTeam.value) {
    payload.team_id = null;
  }

  emit('save', payload);
};
</script>

<style scoped>
:deep(.v-color-picker-edit .v-btn) {
  display: none;
}
</style>
