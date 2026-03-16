require('dotenv').config();

const express = require('express');
const app = express();

const connectDB = require('./db/config');
const authRoutes = require('./routes/authRoutes');

connectDB();

app.use(express.json());

app.use('/auth', authRoutes);

app.listen(process.env.PORT, () => console.log("Server started"));