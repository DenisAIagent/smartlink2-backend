// Script pour ajouter plus de SmartLinks d'exemple réalistes
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const mongoose = require('mongoose');

const artistSchema = new mongoose.Schema({
  name: String,
  slug: String,
  bio: String,
  profileImageUrl: String,
  socialLinks: Object,
  createdAt: { type: Date, default: Date.now }
});

const smartLinkSchema = new mongoose.Schema({
  trackTitle: String,
  artistId: { type: mongoose.Schema.Types.ObjectId, ref: 'Artist' },
  slug: String,
  description: String,
  coverImageUrl: String,
  releaseDate: Date,
  platformLinks: Array,
  isPublished: { type: Boolean, default: true },
  viewCount: { type: Number, default: 0 },
  platformClickCount: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

const Artist = mongoose.model('Artist', artistSchema);
const SmartLink = mongoose.model('SmartLink', smartLinkSchema);

// Nouveaux artistes réalistes
const newArtistsData = [
  {
    name: "Marie Dubois",
    slug: "marie-dubois",
    bio: "Auteure-compositrice-interprète française, mélange pop moderne et influences folk.",
    profileImageUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/marieduboismusic",
      spotify: "https://open.spotify.com/artist/mariedubois"
    }
  },
  {
    name: "The Midnight Riders",
    slug: "the-midnight-riders",
    bio: "Groupe de country-rock français avec des influences américaines authentiques.",
    profileImageUrl: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/midnightriders",
      facebook: "https://facebook.com/midnightriders"
    }
  },
  {
    name: "Elektra",
    slug: "elektra",
    bio: "Productrice et DJ spécialisée dans la techno mélodique et l'ambient.",
    profileImageUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop&crop=face",
    socialLinks: {
      instagram: "https://instagram.com/elektramusic",
      soundcloud: "https://soundcloud.com/elektra"
    }
  }
];

// Nouveaux SmartLinks avec plus de variété
const getNewSmartLinksData = (existingArtists, newArtists) => {
  const allArtists = [...existingArtists, ...newArtists];
  const artistMap = {};
  allArtists.forEach(artist => {
    artistMap[artist.slug] = artist._id;
  });

  return [
    {
      trackTitle: "L'Été Dernier",
      artistSlug: "marie-dubois",
      slug: "ete-dernier",
      description: "Une chanson nostalgique qui évoque les souvenirs d'un été qui s'achève, portée par la voix délicate de Marie Dubois.",
      coverImageUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-06-21'),
      platformLinks: [
        { platform: "Spotify", url: "https://open.spotify.com/track/marie-dubois-ete-dernier" },
        { platform: "Apple Music", url: "https://music.apple.com/fr/album/ete-dernier" },
        { platform: "Deezer", url: "https://deezer.com/track/marie-dubois-ete-dernier" },
        { platform: "YouTube Music", url: "https://music.youtube.com/watch?v=marie-ete-dernier" }
      ],
      viewCount: 1456,
      platformClickCount: 623
    },
    {
      trackTitle: "Highway to Nowhere",
      artistSlug: "the-midnight-riders",
      slug: "highway-to-nowhere",
      description: "Road song épique des Midnight Riders, parfaite pour les escapades sur les routes de campagne.",
      coverImageUrl: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-05-15'),
      platformLinks: [
        { platform: "Spotify", url: "https://open.spotify.com/track/midnight-riders-highway-nowhere" },
        { platform: "Apple Music", url: "https://music.apple.com/fr/album/highway-to-nowhere" },
        { platform: "Amazon Music", url: "https://music.amazon.fr/albums/highway-to-nowhere" }
      ],
      viewCount: 2847,
      platformClickCount: 1124
    },
    {
      trackTitle: "Neon Dreams",
      artistSlug: "elektra",
      slug: "neon-dreams",
      description: "Track techno hypnotique d'Elektra, fusion parfaite entre mélodies éthérées et beats puissants.",
      coverImageUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-04-10'),
      platformLinks: [
        { platform: "Beatport", url: "https://beatport.com/track/elektra-neon-dreams" },
        { platform: "SoundCloud", url: "https://soundcloud.com/elektra/neon-dreams" },
        { platform: "Spotify", url: "https://open.spotify.com/track/elektra-neon-dreams" }
      ],
      viewCount: 3924,
      platformClickCount: 1567
    },
    // Plus de tracks pour les artistes existants
    {
      trackTitle: "Rebel Heart",
      artistSlug: "sidilarsen",
      slug: "rebel-heart",
      description: "Deuxième single de Sidilarsen, un rock anthem qui parle de liberté et de rébellion contre l'conformisme.",
      coverImageUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-03-20'),
      platformLinks: [
        { platform: "Spotify", url: "https://open.spotify.com/track/sidilarsen-rebel-heart" },
        { platform: "Apple Music", url: "https://music.apple.com/fr/album/rebel-heart" },
        { platform: "Deezer", url: "https://deezer.com/track/sidilarsen-rebel-heart" }
      ],
      viewCount: 1876,
      platformClickCount: 734
    },
    {
      trackTitle: "Electric Pulse",
      artistSlug: "outed",
      slug: "electric-pulse",
      description: "Nouveau titre électro-pop d'OUTED avec des influences synthwave et des textures sonores innovantes.",
      coverImageUrl: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-02-14'),
      platformLinks: [
        { platform: "Spotify", url: "https://open.spotify.com/track/outed-electric-pulse" },
        { platform: "Bandcamp", url: "https://outed.bandcamp.com/track/electric-pulse" },
        { platform: "SoundCloud", url: "https://soundcloud.com/outed/electric-pulse" }
      ],
      viewCount: 2341,
      platformClickCount: 892
    },
    {
      trackTitle: "Underground Kingdom",
      artistSlug: "dj-nexus",
      slug: "underground-kingdom",
      description: "Track techno underground de DJ Nexus, parfait pour les sets de fin de soirée dans les clubs alternatifs.",
      coverImageUrl: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop",
      releaseDate: new Date('2024-01-30'),
      platformLinks: [
        { platform: "Beatport", url: "https://beatport.com/track/dj-nexus-underground-kingdom" },
        { platform: "Traxsource", url: "https://traxsource.com/track/dj-nexus-underground-kingdom" },
        { platform: "SoundCloud", url: "https://soundcloud.com/djnexus/underground-kingdom" }
      ],
      viewCount: 4523,
      platformClickCount: 1876
    }
  ].map(smartlink => ({
    ...smartlink,
    artistId: artistMap[smartlink.artistSlug]
  })).map(smartlink => {
    delete smartlink.artistSlug;
    return smartlink;
  });
};

async function addMoreSmartLinks() {
  try {
    console.log('🔄 Connexion à MongoDB...');
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ Connecté à MongoDB');

    // Récupérer les artistes existants
    const existingArtists = await Artist.find({});
    console.log(`📋 ${existingArtists.length} artistes existants trouvés`);

    // Créer les nouveaux artistes
    console.log('👨‍🎤 Création des nouveaux artistes...');
    const newArtists = await Artist.insertMany(newArtistsData);
    console.log(`✅ ${newArtists.length} nouveaux artistes créés`);

    // Créer les nouveaux SmartLinks
    console.log('🔗 Création des nouveaux SmartLinks...');
    const newSmartLinksData = getNewSmartLinksData(existingArtists, newArtists);
    const newSmartLinks = await SmartLink.insertMany(newSmartLinksData);
    console.log(`✅ ${newSmartLinks.length} nouveaux SmartLinks créés`);

    // Statistiques finales
    const totalArtists = await Artist.countDocuments();
    const totalSmartLinks = await SmartLink.countDocuments();

    console.log('\n🎉 Base de données enrichie avec succès !');
    console.log('\n📊 Statistiques finales :');
    console.log(`- ${totalArtists} artistes au total`);
    console.log(`- ${totalSmartLinks} SmartLinks au total`);
    console.log('\n🔗 Accédez à l\'admin : https://www.mdmcmusicads.com/#/admin/smartlinks');

    await mongoose.connection.close();
    console.log('✅ Connexion fermée');

  } catch (error) {
    console.error('❌ Erreur:', error);
    process.exit(1);
  }
}

addMoreSmartLinks();