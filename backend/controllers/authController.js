const bcrypt = require('bcryptjs')
const asyncHandler = require('express-async-handler')
const User = require('../models/User')
const generateToken = require('../helpers/tokenhandler')

const serviceIdPattern = /^[A-Za-z0-9_]+$/
const mobilePattern = /^[6-9]\d{9}$/

const buildUserResponse = (user) => ({
  id: user._id,
  serviceId: user.serviceId,
  mobileNumber: user.mobileNumber,
  name: user.name,
  email: user.email,
  username: user.username,
  stationName: user.stationName,
  location: user.location,
  imageUrl: user.imageUrl,
})

const normalizeMobileNumber = (mobileNumber) => {
  const digits = String(mobileNumber || '').replace(/\D/g, '')
  return digits.length === 12 && digits.startsWith('91') ? digits.slice(2) : digits
}

const registerUser = asyncHandler(async (req, res) => {
  const { serviceId, mobileNumber, password } = req.body

  if (!serviceId || !mobileNumber || !password) {
    res.status(400)
    throw new Error('Please add all fields')
  }

  const cleanServiceId = serviceId.trim()
  const cleanMobileNumber = normalizeMobileNumber(mobileNumber)

  if (!serviceIdPattern.test(cleanServiceId)) {
    res.status(400)
    throw new Error('Service ID can include letters, numbers, and underscores only')
  }

  if (!mobilePattern.test(cleanMobileNumber)) {
    res.status(400)
    throw new Error('Please provide a valid 10-digit mobile number')
  }

  const userExists = await User.findOne({ serviceId: cleanServiceId })
  if (userExists) {
    res.status(400)
    throw new Error('User already exists with this Service ID')
  }

  const salt = await bcrypt.genSalt(10)
  const hashedPassword = await bcrypt.hash(password, salt)

  const user = await User.create({
    serviceId: cleanServiceId,
    mobileNumber: cleanMobileNumber,
    password: hashedPassword,
    name: cleanServiceId,
    username: cleanServiceId,
  })

  res.status(201).json({
    message: 'User registered successfully',
    user: buildUserResponse(user),
    token: generateToken(user._id),
  })
})
const loginUser = asyncHandler(async (req, res) => {
  const { serviceId, password } = req.body

  if (!serviceId || !password) {
    res.status(400)
    throw new Error('Please provide Service ID and password')
  }

  const user = await User.findOne({ serviceId: serviceId.trim() })

  if (user && (await bcrypt.compare(password, user.password))) {
    res.json({
      user: buildUserResponse(user),
      token: generateToken(user._id),
    })
  } else {
    res.status(400)
    throw new Error('Invalid credentials')
  }
})

const getMe = asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id)

  if (!user) {
    res.status(404)
    throw new Error('User not found')
  }

  res.status(200).json(buildUserResponse(user))
})

const updateProfile = asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id)

  if (!user) {
    res.status(404)
    throw new Error('User not found')
  }

  const {
    name,
    email,
    mobileNumber,
    phone,
    username,
    stationName,
    location,
    imageUrl,
  } = req.body

  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
    res.status(400)
    throw new Error('Please provide a valid email address')
  }

  const nextMobileNumber = mobileNumber || phone
  if (nextMobileNumber) {
    const cleanMobileNumber = normalizeMobileNumber(nextMobileNumber)
    if (!mobilePattern.test(cleanMobileNumber)) {
      res.status(400)
      throw new Error('Please provide a valid 10-digit mobile number')
    }
    user.mobileNumber = cleanMobileNumber
  }

  if (name !== undefined) user.name = name.trim()
  if (email !== undefined) user.email = email.trim()
  if (username !== undefined) user.username = username.trim()
  if (stationName !== undefined) user.stationName = stationName.trim()
  if (location !== undefined) user.location = location.trim()
  if (imageUrl !== undefined) user.imageUrl = imageUrl.trim()

  const updatedUser = await user.save()

  res.status(200).json({
    message: 'Profile updated successfully',
    user: buildUserResponse(updatedUser),
  })
})



module.exports = { registerUser, loginUser, getMe, updateProfile };
