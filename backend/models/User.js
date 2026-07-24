const mongoose = require('mongoose')

const UserSchema = mongoose.Schema(
  {
    // Police / Service ID 
    serviceId: {
      type: String,
      required: [true, 'Please add your Service ID'],
      trim: true,
      validate: {
        validator: function (v) {
          return /^[A-Za-z0-9_]+$/.test(v)
        },
        message: 'Service ID can include letters, numbers, and underscores only',
      },
    },
  
    mobileNumber: {
      type: String,
      required: [true, 'Please add your Mobile Number'],
      trim: true,
    },
    password: {
      type: String,
      required: [true, 'Please add a password'],
    },
    name: {
      type: String,
      trim: true,
      default: '',
    },
    email: {
      type: String,
      trim: true,
      lowercase: true,
      default: '',
    },
    username: {
      type: String,
      trim: true,
      default: '',
    },
    stationName: {
      type: String,
      trim: true,
      default: '',
    },
    location: {
      type: String,
      trim: true,
      default: '',
    },
    imageUrl: {
      type: String,
      trim: true,
      default: 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
    },
  },
  {
    timestamps: true,
  }
)

module.exports = mongoose.model('User', UserSchema)
