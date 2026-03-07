const express = require('express')
const router = express.Router()
const { registerUser, loginUser, getMe } = require('../controllers/authController')
router.post('/reg', registerUser)
router.get('/me', getMe)
router.post('/login', loginUser)
module.exports = router;