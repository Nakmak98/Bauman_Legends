<template>
    <div class="basic-block">
        <div v-if="game">
            <play-state v-if="game.status === 'PLAY'"
                        :game="game"
                        :status="status">
            </play-state>
            <pause-state v-if="game.status === 'PAUSE'"
                         :game="game"
                         :status="status">
            </pause-state>
            <stop-state v-if="game.status === 'STOP'"
                        :game="game"
                        :status="status">
            </stop-state>
        </div>
        <div v-else>
            Загружаем задание...
        </div>
    </div>
</template>

<script>
    import PauseState from "../../components/player/PauseState";
    import StopState from "../../components/player/StopState";
    import PlayState from "../../components/player/PlayState";
    import {ErrorHandler} from "../../ErrorHandler";
    import Axios from 'axios'
    export default {
        name: "Game",
        components: {
            PauseState,
            PlayState,
            StopState
        },
        data() {
          return {
              status: null
          }
        },
        computed: {
          game() { return this.$store.state.game }
        },
        mounted() {
            this.request_game_status();
            this.$store.dispatch('updateTaskStatus', undefined, this)
        },
        beforeDestroy() {
            if (this.$store.state.error.message !== null)
                this.$store.commit('deleteErrorMessage')
        },
        methods: {
            request_game_status() {
                Axios
                    .get('/game/status')
                    .then(response => {
                        this.$store.commit('deleteErrorMessage');
                        this.status = response.data;
                    })
                    .catch(error => {
                        if(error.response){
                            new ErrorHandler(error.response, this)
                        } else {
                            this.$router.push("/connection_error");
                        }
                    })
            },
        }
    }
</script>

<style scoped>
</style>