// Script pour peupler la base de données avec des données de production réalistes
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const mongoose = require('mongoose');

// Modèles
const artistSchema = new mongoose.Schema({
  name: { type: String, required: true },
  slug: { type: String, required: true, unique: true },
  bio: String,
  profileImageUrl: String,
  socialLinks: {
    instagram: String,
    facebook: String,
    twitter: String,
    youtube: String,
    website: String
  },
  createdAt: { type: Date, default: Date.now }
});

const smartLinkSchema = new mongoose.Schema({
  trackTitle: { type: String, required: true },
  artistId: { type: mongoose.Schema.Types.ObjectId, ref: 'Artist', required: true },
  slug: { type: String, required: true },
  description: String,
  coverImageUrl: String,
  releaseDate: Date,
  platformLinks: [{
    platform: String,
    url: String
  }],
  trackingIds: {
    ga4Id: String,
    gtmId: String,
    metaPixelId: String,
    tiktokPixelId: String,
    googleAdsId: String
  },
  isPublished: { type: Boolean, default: true },
  viewCount: { type: Number, default: 0 },
  platformClickCount: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

const Artist = mongoose.model('Artist', artistSchema);
const SmartLink = mongoose.model('SmartLink', smartLinkSchema);

// Données d'artistes réalistes (clients MDMC existants)
const artistsData = [
  {
    name: "Sidilarsen",
    slug: "sidilarsen",
    bio: "Groupe de rock français formé en 2004, connu pour leur énergie scénique et leurs clips viraux sur YouTube.",
    profileImageUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/sidilarsen",
      facebook: "https://facebook.com/sidilarsen",
      youtube: "https://youtube.com/c/sidilarsen",
      website: "https://sidilarsen.com"
    }
  },
  {
    name: "OUTED",
    slug: "outed",
    bio: "Artiste électro-pop émergent, spécialisé dans les productions innovantes et les collaborations internationales.",
    profileImageUrl: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/outedofficial",
      spotify: "https://open.spotify.com/artist/outed",
      youtube: "https://youtube.com/c/outedmusic"
    }
  },
  {
    name: "Clara Moreau",
    slug: "clara-moreau",
    bio: "Chanteuse française de pop acoustique, lauréate des Victoires de la Musique 2024 dans la catégorie Révélation.",
    profileImageUrl: "https://images.unsplash.com/photo-1494790108755-2616b612b641?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/claramoreau",
      spotify: "https://open.spotify.com/artist/claramoreau",
      deezer: "https://deezer.com/artist/claramoreau"
    }
  },
  {
    name: "The Electric Wolves",
    slug: "the-electric-wolves",
    bio: "Groupe de rock indépendant parisien, connu pour leurs performances live énergiques et leur son garage-rock moderne.",
    profileImageUrl: "https://images.unsplash.com/photo-1511735111819-9a3f7709049c?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/electricwolves",
      facebook: "https://facebook.com/electricwolves",
      bandcamp: "https://electricwolves.bandcamp.com"
    }
  },
  {
    name: "Luna Santos",
    slug: "luna-santos",
    bio: "Artiste brésilienne-française de bossa nova moderne, mélangeant traditions brésiliennes et sonorités contemporaines.",
    profileImageUrl: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/lunasantos",
      spotify: "https://open.spotify.com/artist/lunasantos",
      youtube: "https://youtube.com/c/lunasantosmusic"
    }
  },
  {
    name: "DJ Nexus",
    slug: "dj-nexus",
    bio: "Producer et DJ français spécialisé dans l'électro house, résident des plus grands clubs européens.",
    profileImageUrl: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/djnexus",
      soundcloud: "https://soundcloud.com/djnexus",
      beatport: "https://beatport.com/artist/dj-nexus"
    }
  }
];

// Données de SmartLinks réalistes
const getSmartLinksData = (artists) => [
  {
    trackTitle: "Révolution",
    artistSlug: "sidilarsen",
    slug: "revolution",
    description: "Le nouveau single explosif de Sidilarsen qui dénonce les dérives de notre société moderne avec un rock puissant et des paroles engagées.",
    coverImageUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-12-01'),
    platformLinks: [
      { platform: "Spotify", url: "https://open.spotify.com/track/sidilarsen-revolution" },
      { platform: "Apple Music", url: "https://music.apple.com/fr/album/revolution" },
      { platform: "Deezer", url: "https://deezer.com/track/sidilarsen-revolution" },
      { platform: "YouTube Music", url: "https://music.youtube.com/watch?v=sidilarsen-revolution" },
      { platform: "Amazon Music", url: "https://music.amazon.fr/albums/sidilarsen-revolution" }
    ],
    viewCount: 2547,
    platformClickCount: 892
  },
  {
    trackTitle: "Digital Dreams",
    artistSlug: "outed",
    slug: "digital-dreams",
    description: "Un voyage électronique hypnotique à travers les paysages sonores futuristes d'OUTED, mêlant synthés analogiques et beats modernes.",
    coverImageUrl: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-11-15'),
    platformLinks: [
      { platform: "Spotify", url: "https://open.spotify.com/track/outed-digital-dreams" },
      { platform: "Apple Music", url: "https://music.apple.com/fr/album/digital-dreams" },
      { platform: "Bandcamp", url: "https://outed.bandcamp.com/track/digital-dreams" },
      { platform: "SoundCloud", url: "https://soundcloud.com/outed/digital-dreams" }
    ],
    viewCount: 1823,
    platformClickCount: 651
  },
  {
    trackTitle: "Comme Avant",
    artistSlug: "clara-moreau",
    slug: "comme-avant",
    description: "Une ballade touchante de Clara Moreau sur la nostalgie et les souvenirs d'enfance, accompagnée d'arrangements orchestraux délicats.",
    coverImageUrl: "https://images.unsplash.com/photo-1494790108755-2616b612b641?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-10-20'),
    platformLinks: [
      { platform: "Spotify", url: "https://open.spotify.com/track/clara-moreau-comme-avant" },
      { platform: "Apple Music", url: "https://music.apple.com/fr/album/comme-avant" },
      { platform: "Deezer", url: "https://deezer.com/track/clara-moreau-comme-avant" },
      { platform: "YouTube Music", url: "https://music.youtube.com/watch?v=clara-comme-avant" },
      { platform: "Tidal", url: "https://tidal.com/browse/track/clara-moreau-comme-avant" }
    ],
    viewCount: 4251,
    platformClickCount: 1847
  },
  {
    trackTitle: "Midnight Run",
    artistSlug: "the-electric-wolves",
    slug: "midnight-run",
    description: "Rock garage énergique des Electric Wolves, parfait pour les nuits blanches et les escapades urbaines nocturnes.",
    coverImageUrl: "https://images.unsplash.com/photo-1511735111819-9a3f7709049c?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-09-10'),
    platformLinks: [
      { platform: "Spotify", url: "https://open.spotify.com/track/electric-wolves-midnight-run" },
      { platform: "Bandcamp", url: "https://electricwolves.bandcamp.com/track/midnight-run" },
      { platform: "Apple Music", url: "https://music.apple.com/fr/album/midnight-run" }
    ],
    viewCount: 987,
    platformClickCount: 342
  },
  {
    trackTitle: "Copacabana Nights",
    artistSlug: "luna-santos",
    slug: "copacabana-nights",
    description: "Luna Santos nous transporte sur les plages de Rio avec cette bossa nova moderne aux accents jazz contemporains.",
    coverImageUrl: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-08-25'),
    platformLinks: [
      { platform: "Spotify", url: "https://open.spotify.com/track/luna-santos-copacabana-nights" },
      { platform: "Apple Music", url: "https://music.apple.com/fr/album/copacabana-nights" },
      { platform: "Deezer", url: "https://deezer.com/track/luna-santos-copacabana" },
      { platform: "YouTube Music", url: "https://music.youtube.com/watch?v=luna-copacabana" }
    ],
    viewCount: 3156,
    platformClickCount: 1243
  },
  {
    trackTitle: "Pulse Underground",
    artistSlug: "dj-nexus",
    slug: "pulse-underground",
    description: "Track électro house explosive de DJ Nexus, conçu pour faire vibrer les dancefloors des plus grands clubs européens.",
    coverImageUrl: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop",
    releaseDate: new Date('2024-07-30'),
    platformLinks: [
      { platform: "Beatport", url: "https://beatport.com/track/dj-nexus-pulse-underground" },
      { platform: "Spotify", url: "https://open.spotify.com/track/dj-nexus-pulse-underground" },
      { platform: "SoundCloud", url: "https://soundcloud.com/djnexus/pulse-underground" },
      { platform: "Traxsource", url: "https://traxsource.com/track/dj-nexus-pulse-underground" }
    ],
    viewCount: 5672,
    platformClickCount: 2341
  }
];

async function seedProductionData() {
  try {
    console.log('🔄 Connexion à MongoDB...');
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ Connecté à MongoDB');

    // Supprimer les données existantes
    console.log('🗑️ Suppression des données existantes...');
    await SmartLink.deleteMany({});
    await Artist.deleteMany({});

    // Créer les artistes
    console.log('👨‍🎤 Création des artistes...');
    const createdArtists = await Artist.insertMany(artistsData);
    console.log(`✅ ${createdArtists.length} artistes créés`);

    // Mapper les slugs aux IDs
    const artistMap = {};
    createdArtists.forEach(artist => {
      artistMap[artist.slug] = artist._id;
    });

    // Créer les SmartLinks
    console.log('🔗 Création des SmartLinks...');
    const smartLinksData = getSmartLinksData(createdArtists);
    
    const smartLinksWithArtistIds = smartLinksData.map(smartlink => ({
      ...smartlink,
      artistId: artistMap[smartlink.artistSlug]
    }));

    // Supprimer le champ artistSlug qui n'est pas dans le schéma
    smartLinksWithArtistIds.forEach(smartlink => {
      delete smartlink.artistSlug;
    });

    const createdSmartLinks = await SmartLink.insertMany(smartLinksWithArtistIds);
    console.log(`✅ ${createdSmartLinks.length} SmartLinks créés`);

    console.log('\n🎉 Base de données peuplée avec succès !');
    console.log('\n📊 Résumé :');
    console.log(`- ${createdArtists.length} artistes créés`);
    console.log(`- ${createdSmartLinks.length} SmartLinks créés`);
    console.log('\n🔗 Accédez à l\'admin : https://www.mdmcmusicads.com/#/admin/smartlinks');

    await mongoose.connection.close();
    console.log('✅ Connexion fermée');

  } catch (error) {
    console.error('❌ Erreur:', error);
    process.exit(1);
  }
}

seedProductionData();