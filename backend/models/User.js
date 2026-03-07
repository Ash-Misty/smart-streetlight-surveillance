const mongoose = require('mongoose')
const UserSchema=mongoose.Schema({
    name:{
        type:String,
        required:[true,'Please add name']
    },
    email:{
        type:String,
        required:[true,'Please add email']
    },
    password:{
        type:String,
        required:[true,'please add a password']
    }
},{
    timestamps:{
        required:true
    }
})
module.exports=mongoose.model("User",UserSchema)