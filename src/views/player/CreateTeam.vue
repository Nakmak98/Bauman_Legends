<template>
    <div id="create-team" class="basic-block">
        <h1>Создание команды</h1>
        <base-input type="text" placeholder="Название команды" v-model="team_name"></base-input>
        <base-button title="Создать" @click="check_create_team"></base-button>
    </div>
</template>

<script>
    import Axios from 'axios'
    import {ErrorHandler} from "../../ErrorHandler";

    export default {
        name: "CreateTeam",
        data() {
            return {
                team_name: '',
            }
        },
        beforeDestroy() {
            if(this.$store.state.error.message !== null)
                this.$store.commit('deleteErrorMessage')
        },
        methods: {
            check_create_team: function () {
                if (this.team_name !== '') {
                    this.create_team();
                } else {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Поле не должно быть пустым."
                    });
                }
            },
            create_team: function () {
                Axios
                    .post('/team/create', {
                        team_name: this.team_name
                    })
                    .then(response => {
                        this.$store.commit('setTeamData', response.data);
                        this.$store.dispatch('updateUserData');
                        this.$router.push('/team');
                    })
                    .catch(error => {
                        if(error.response) {
                           new ErrorHandler(error.response, this)
                       } else {
                            this.$router.push("/connection_error");
                        }
                    })
            }
        }
    }
</script>