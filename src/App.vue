<template>
    <div id="app">
        <base-popup></base-popup>
        <nav-bar></nav-bar>
        <router-view/>
        <base-error-message></base-error-message>
    </div>
</template>

<script>
    import NavBar from "./components/NavBar";
    export default {
        name: 'app',
        components: {NavBar},
    }
</script>

<style lang="scss">
    * {
        font-family: 'Neucha', cursive;
        font-size: 18px;
    }
    p {
        word-wrap: break-word;
        margin: 4px 1px;
    }

    h1 {
        font-family: BemountLine;
        font-weight: 500;
        margin-top: 5px;
        font-size: 48px;
    }

    @font-face {
        font-family: BemountLine;
        src: url("assets/Bemount-Line.woff") format("woff"), url("assets/Bemount-Line.otf") format("truetype");
    }

    body {
        height: 100vh;
        margin: 0;
        background-color: #fdf8ed;
    }

    .basic-block {
        padding: 10px;
        max-width: 800px;
        margin: 0 auto;
        background-color: #f8e0be;
        border-radius: 20px;
        border: 10px solid #e1bf92;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.3);
        color: black;
    }

    #app {
        height: 100%;
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        padding: 0 10px;
        background: url("assets/bg1.png") no-repeat;
        background-size: cover;
    }

    #ornament-top {
        position: absolute;
        left: -15px;
        top: -55px;
        width: 310px;
    }

    #ornament-bottom {
        position: absolute;
        left: 0;
        bottom: -30px;
        width: 280px;
    }

    .auth {
        box-sizing: border-box;
        width: 300px;
        min-height: 300px;
        margin: 100px auto 0;
        position: relative;
        max-width: 400px;
        padding: 20px 10px;
    }

    button {
        height: 40px;
        border-radius: 10px;
        background: #fff;
        border: none;
        width: 200px;
        margin-bottom: 5px;
        font-size: 20px;
    }

    table {
        min-width: 195px;
        background-color: #9b7c55;
        margin: 0 auto 19px;
    }

    .table-xxl {
        width: -webkit-fill-available;
    }
    .table-block-xxl{
        height: 50px;
    }

    .table-cont {
        background-color: #ffedd4;

    }

    p > img {
        max-width: 100%;
    }

    .clickable {
        cursor: pointer;
    }
</style>
