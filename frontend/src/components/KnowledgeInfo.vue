<template>

<el-card class="info">


<h2>
{{ node.name }}
</h2>



<p>
掌握程度：
{{ node.level }}%
</p>



<p>
AI建议：
{{ node.advice }}
</p>



</el-card>


</template>



<script setup>


defineProps({

node:{

type:Object,

default:()=>({

name:"",

level:0,

advice:""

})

}

})


</script>



<style scoped>


.info{

width:280px;

height:220px;

}


</style>