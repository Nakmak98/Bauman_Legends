<template>
   <div>
      <game-tooltip :show="show_tooltip" @close-tooltip="show_tooltip=false"></game-tooltip>
      <p class="ql-editor" v-html="game.task.html"></p>
      <p>
         <timer :start_time="game.task.start_time"
                :duration="game.task.duration"
                v-if="game.task.duration">
         </timer>
      </p>
      <p>Баллов за задание: {{game.task.points}}</p>
      <p><base-input type="text" placeholder="Ответ" v-model="answer"></base-input></p>
      <br>
      <p><base-button title="Отправить" @click="send_answer"></base-button></p>
      <p><base-button v-if="game.task.skip && user.role === 'CAPTAIN'" title="Пропустить" @click="check_skip"></base-button></p>
      <p><base-button v-if="status === 'FINAL'" title="Подсказка" @click="show_tooltip = true"></base-button></p>
   </div>
</template>

<script>
    import Timer from "./Timer";
    import GameTooltip from "./GameTooltip";
    import {ErrorHandler} from "../../ErrorHandler";
    import Axios from 'axios';
    export default {
        name: "PlayState",
        components: {
           Timer,
           GameTooltip
        },
        props: {
           status: String
        },
        data() {
            return {
               timer: null,
               answer: '',
               show_tooltip: false
            }
        },
        computed: {
           user() { return this.$store.state.user },
           game() { return this.$store.state.game }
        },
        methods: {
            check_skip() {
               let popup_options = {
                  message: "Вы уверены, что хотите пропустить задание? Вернуться к нему будет невозможно.",
                  show: true,
                  callback: this.skip_task,
                  args: null
               };
               this.$store.commit('deleteErrorMessage');
               this.$store.commit('setPopupOptions', popup_options)
            },
            skip_task() {
               Axios
                       .get('/game/skip')
                       .then(() => {
                          this.$store.dispatch('updateTaskStatus', undefined, this)
                       })
                       .catch(error => {
                          if(error.response) {
                             new ErrorHandler(error.response, this)
                          } else {
                             this.$router.push('/connection_error')
                          }
                       })
            },
            send_answer() {
               if(this.answer === ''){
                  this.$store.commit('setErrorMessage', {
                     message: "Нельзя отослать пустой ответ"
                  });
                  return
               }
               Axios
                       .post('/game/answer', {
                          team_id: this.user.team_id,
                          task_id: this.game.task.task_id,
                          answer: this.answer
                       })
                       .then(() => {
                          this.$store.dispatch('updateTaskStatus', undefined, this)
                       })
                       .catch(error => {
                          if(error.response.status === 400) {
                             let popup_options = {
                                header: false,
                                message: error.response.data.message,
                                show: true,
                                callback: null,
                                args: null
                             };
                             this.$store.commit('deleteErrorMessage');
                             this.$store.commit('setPopupOptions', popup_options);
                             return;
                          }
                          if(error.response) {
                             new ErrorHandler(error.response, this)
                          } else {
                             this.$router.push('/connection_error')
                          }
                       })
            }
        }
    }
</script>

<style scoped>

</style>