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
          return /^[A-Za-z0-9 ]+$/.test(v)
        },
        message: 'Service ID must be alphanumeric and can include spaces only',
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
  },
  {
    timestamps: true,
  }
)

module.exports = mongoose.model('User', UserSchema)