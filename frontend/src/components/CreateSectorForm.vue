<template>
  <v-form ref="form" @submit.prevent="saveSector">
    <v-container>
      <v-row>
        <v-col cols="12" class="py-2">
          <v-text-field
            v-model="formData.name"
            label="Название участка"
            :rules="[requiredRule]"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-text-field>
        </v-col>

        <v-col cols="12" class="py-2" v-if="props.showCuratorSelection">
          <v-select
            v-model="formData.curator_id"
            :items="props.curators"
            item-title="fullname"
            item-value="id"
            label="Куратор"
            :rules="[requiredRule]"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-select>
        </v-col>

        <v-col cols="12" class="py-2" v-if="props.showCuratorSelection">
          <v-checkbox
            v-model="assignTeam"
            label="Назначить команду"
            density="compact"
            hide-details="auto"
          ></v-checkbox>
        </v-col>

        <v-col cols="12" class="py-2" v-if="assignTeam">
          <v-select
            v-model="formData.team_id"
            :items="props.teams"
            item-title="name"
            item-value="id"
            label="Команда"
            :rules="assignTeam ? [requiredRule] : []"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-select>
        </v-col>

        <v-col cols="12" class="py-2">
          <p class="text-body-2 mt-2 mb-1">Цвет участка</p>
          <v-color-picker
            v-model="formData.color"
            mode="hex"
            hide-canvas
            hide-alpha
            width="100%"
          ></v-color-picker>
        </v-col>
      </v-row>
    </v-container>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="cancel">Отмена</v-btn>
      <v-btn color="primary" variant="flat" type="submit">Сохранить</v-btn>
    </v-card-actions>
  </v-form>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useUiStore } from "@/stores/uiStore";

const props = defineProps({
  curators: { type: Array, required: true },
  teams: { type: Array, default: () => [] },
  geometry: { type: Object, default: null },
  showCuratorSelection: { type: Boolean, default: true },
  preselectedCuratorId: { type: Number, default: null },
  sectorData: { type: Object, default: null },
  initialColor: { type: String, default: "#1DE9B6" },
  onSave: { type: Function, required: true },
});

const uiStore = useUiStore();

const form = ref(null);
const assignTeam = ref(false);
const formData = ref({});
const initialFormDataString = ref("");

const isFormDirty = computed(() => {
  return JSON.stringify(formData.value) !== initialFormDataString.value;
});

watch(isFormDirty, (isDirty) => {
  uiStore.setFormDirty(isDirty);
});

const requiredRule = (v) => !!v || "Поле обязательно для заполнения";

const updateFormData = (data) => {
  const newFormData = {};
  if (data) {
    newFormData.name = data.name;
    newFormData.color = data.color;
    newFormData.curator_id = data.curator.id;
    if (data.team) {
      newFormData.team_id = data.team.id;
      assignTeam.value = true;
    } else {
      newFormData.team_id = null;
      assignTeam.value = false;
    }
  } else {
    newFormData.name = "";
    newFormData.color = props.initialColor;
    newFormData.curator_id =
      !props.showCuratorSelection && props.preselectedCuratorId
        ? props.preselectedCuratorId
        : null;
    newFormData.team_id = null;
    assignTeam.value = false;
  }
  formData.value = newFormData;
  initialFormDataString.value = JSON.stringify(newFormData);
};

watch(
  () => props.sectorData,
  (newSectorData) => {
    updateFormData(newSectorData);
  },
  { immediate: true }
);

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

  props.onSave(payload);
};
</script>

<style scoped>
:deep(.v-color-picker-edit .v-btn) {
  display: none;
}
:deep(.v-color-picker-canvas) {
  padding: 10px 0;
}
:deep(.v-field__input) {
  font-size: 0.875rem !important;
}
:deep(.v-label.v-field-label) {
  font-size: 0.875rem !important;
}
</style>
