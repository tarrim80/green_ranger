<template>
  <v-dialog :model-value="modelValue" @update:model-value="closeDialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Создание нового участка</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="sectorName"
                  label="Название участка"
                  :rules="[requiredRule]"
                  required
                ></v-text-field>
              </v-col>

              <v-col cols="12" v-if="showCuratorSelection">
                <v-select
                  v-model="selectedCurator"
                  :items="curators"
                  item-title="fullname"
                  item-value="id"
                  label="Куратор"
                  :rules="[requiredRule]"
                  required
                ></v-select>
              </v-col>

              <v-col cols="12" v-if="showCuratorSelection">
                <v-checkbox
                  v-model="assignTeam"
                  label="Назначить команду"
                ></v-checkbox>
              </v-col>

              <v-col cols="12" v-if="assignTeam">
                <v-select
                  v-model="selectedTeam"
                  :items="teams"
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
                  v-model="sectorColor"
                  mode="hex"
                  hide-alpha
                  width="400"
                ></v-color-picker>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="closeDialog">
          Отмена
        </v-btn>
        <v-btn color="primary" variant="flat" @click="saveSector">
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  curators: {
    type: Array,
    required: true,
  },
  teams: {
    type: Array,
    default: () => [],
  },
  geometry: {
    type: Object,
    required: true,
  },
  showCuratorSelection: {
    type: Boolean,
    default: true,
  },
  preselectedCuratorId: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits(['update:modelValue', 'save', 'cancel']);

const form = ref(null);
const sectorName = ref('');
const selectedCurator = ref(null);
const sectorColor = ref('#1DE9B6');
const assignTeam = ref(false);
const selectedTeam = ref(null);

const requiredRule = (v) => !!v || 'Поле обязательно для заполнения';

watch(() => props.modelValue, (isOpening) => {
  if (isOpening && !props.showCuratorSelection) {
    selectedCurator.value = props.preselectedCuratorId;
  } else if (!isOpening) {
    sectorName.value = '';
    selectedCurator.value = null;
    sectorColor.value = '#1DE9B6';
    assignTeam.value = false;
    selectedTeam.value = null;
  }
});

const closeDialog = () => {
  emit('update:modelValue', false);
  emit('cancel');
};

const saveSector = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  const sectorData = {
    name: sectorName.value,
    color: sectorColor.value,
    curator_id: selectedCurator.value,
    geometry: props.geometry,
    team_id: assignTeam.value ? selectedTeam.value : null,
  };

  emit('save', sectorData);
  closeDialog();
};
</script>

<style scoped>
:deep(.v-color-picker-edit .v-btn) {
  display: none;
}
</style>
