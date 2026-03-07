const express=require('express')
const app = express()
const connectDB=require('./db/config')
const authRoutes=require('./routes/authRoutes')
require('dotenv').config()
connectDB();
app.use(express.json());
app.use('/auth',authRoutes)
app.listen(process.env.PORT,()=>console.log("Server started"))