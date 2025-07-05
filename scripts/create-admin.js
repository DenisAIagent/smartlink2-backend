// Script pour créer un utilisateur admin temporaire
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

// Modèle User simple
const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['user', 'admin'], default: 'user' },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

async function createAdmin() {
  try {
    // Connexion à MongoDB
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ Connecté à MongoDB');

    // Vérifier si l'admin existe déjà
    const existingAdmin = await User.findOne({ email: 'admin@mdmcmusicads.com' });
    if (existingAdmin) {
      console.log('👤 Utilisateur admin existe déjà');
      
      // Mettre à jour le mot de passe
      const hashedPassword = await bcrypt.hash('admin123', 12);
      await User.findByIdAndUpdate(existingAdmin._id, { 
        password: hashedPassword,
        role: 'admin'
      });
      console.log('🔑 Mot de passe admin mis à jour : admin123');
    } else {
      // Créer un nouvel admin
      const hashedPassword = await bcrypt.hash('admin123', 12);
      
      const admin = new User({
        name: 'Admin MDMC',
        email: 'admin@mdmcmusicads.com',
        password: hashedPassword,
        role: 'admin'
      });

      await admin.save();
      console.log('✅ Utilisateur admin créé avec succès');
    }

    console.log('\n📋 Informations de connexion:');
    console.log('Email: admin@mdmcmusicads.com');
    console.log('Mot de passe: admin123');
    console.log('\n🔗 Connectez-vous via: https://www.mdmcmusicads.com/#/admin/login');

    await mongoose.connection.close();
    console.log('✅ Connexion fermée');
    
  } catch (error) {
    console.error('❌ Erreur:', error);
    process.exit(1);
  }
}

createAdmin();