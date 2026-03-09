const bcrypt = require('bcryptjs')
const asyncHandler = require('express-async-handler')
const User = require('../models/User')
const generateToken = require('../helpers/tokenhandler')

const registerUser = asyncHandler(async (req, res) => {
  const { serviceId, mobileNumber, password } = req.body

  if (!serviceId || !mobileNumber || !password) {
    res.status(400)
    throw new Error('Please add all fields')
  }

  // Enforce Service ID format: alphanumeric with spaces
  const serviceIdPattern = /^[A-Za-z0-9 ]+$/
  if (!serviceIdPattern.test(serviceId)) {
    res.status(400)
    throw new Error('Service ID must be alphanumeric and can include spaces only')
  }

  const userExists = await User.findOne({ serviceId })
  if (userExists) {
    res.status(400)
    throw new Error('User already exists with this Service ID')
  }

  const salt = await bcrypt.genSalt(10)
  const hashedPassword = await bcrypt.hash(password, salt)

  await User.create({
    serviceId,
    mobileNumber,
    password: hashedPassword,
  })

  res.status(201).json({ message: 'User registered successfully' })
})
const loginUser = asyncHandler(async (req, res) => {
  const { serviceId, password } = req.body

  if (!serviceId || !password) {
    res.status(400)
    throw new Error('Please provide Service ID and password')
  }

  const user = await User.findOne({ serviceId })

  if (user && (await bcrypt.compare(password, user.password))) {
    res.json({
      _id: user.id,
      serviceId: user.serviceId,
      mobileNumber: user.mobileNumber,
      token: generateToken(user._id),
    })
  } else {
    res.status(400)
    throw new Error('Invalid credentials')
  }
})

const getMe = asyncHandler(async (req, res) => {
  const { _id, serviceId, mobileNumber } = await User.findById(req.user.id)

  res.status(200).json({
    id: _id,
    serviceId,
    mobileNumber,
  })
})



module.exports = { registerUser, loginUser, getMe};