require('dotenv').config();

const express = require('express');
const cors = require('cors');
const app = express();

const connectDB = require('./db/config');
const authRoutes = require('./routes/authRoutes');

connectDB();

app.use(cors());
app.use(express.json());

app.use('/auth', authRoutes);

app.use((err, req, res, next) => {
  const statusCode = res.statusCode === 200 ? 500 : res.statusCode;

  res.status(statusCode).json({
    message: err.message || 'Server error',
  });
});

const port = process.env.PORT || 5000;

app.listen(port, () => console.log(`Server started on port ${port}`));
