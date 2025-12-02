import React, { useState, useEffect, useRef } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  Animated,
  Easing,
  ImageBackground,
} from 'react-native';
import { request, PERMISSIONS, RESULTS } from 'react-native-permissions';
import Geolocation from 'react-native-geolocation-service';
import LinearGradient from 'react-native-linear-gradient';
import MaskedView from '@react-native-masked-view/masked-view';
import { BlurView } from '@react-native-community/blur';

const { width, height } = Dimensions.get('window');

const QRSApp = () => {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState('');
  const [entropy, setEntropy] = useState('');
  const [coords, setCoords] = useState('Acquiring quantum lock...');

  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;
  const glowValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    request(PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION).then(res => {
      if (res === RESULTS.GRANTED) {
        Geolocation.getCurrentPosition(
          pos => {
            setCoords(`${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`);
          },
          () => setCoords('Quantum flux detected'),
          { enableHighAccuracy: true, timeout: 10000 }
        );
      }
    });
  }, []);

  const startScanning = () => {
    setScanning(true);
    setResult('');
    setEntropy('');

    // Pulsing glow
    Animated.loop(
      Animated.sequence([
        Animated.timing(glowValue, { toValue: 1, duration: 1000, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(glowValue, { toValue: 0.3, duration: 1000, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
      ])
    ).start();

    // Spin wheel
    Animated.timing(spinValue, {
      toValue: 1,
      duration: 4000,
      easing: Easing.linear,
      useNativeDriver: true,
    }).start();

    // Simulate quantum scan
    setTimeout(() => {
      const verdicts = ['Low', 'Medium', 'High'];
      const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
      const score = (Math.random() * 0.6 + 0.3).toFixed(3);
      const states = ['CHAOS RESONANCE', 'TURBULENT FIELD', 'STABLE MANIFOLD'];
      const state = states[Math.floor(Math.random() * states.length)];

      setResult(verdict);
      setEntropy(`${state} ${score}`);
      setScanning(false);
      glowValue.setValue(0);
    }, 5000);
  };

  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '720deg'],
  });

  const getVerdictColor = () => {
    if (result === 'Low') return ['#00ff9d', '#00ffc3'];
    if (result === 'Medium') return ['#ffd000', '#ff8c00'];
    if (result === 'High') return ['#ff2e63', '#ff477e'];
    return ['#8b5cf6', '#6366f1'];
  };

  return (
    <ImageBackground
      source={{ uri: 'https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=800&q=80' }}
      style={styles.background}
      blurRadius={10}
    >
      <SafeAreaView style={styles.container}>
        {/* Floating Glass Header */}
        <BlurView style={styles.headerGlass} blurType="dark" blurAmount={10}>
          <MaskedView
            maskElement={
              <Text style={styles.title}>HYDRA-9</Text>
            }
          >
            <LinearGradient colors={['#8b5cf6', '#ec4899']} style={styles.gradientText} />
          </MaskedView>
          <Text style={styles.subtitle}>Quantum Road Oracle</Text>
        </BlurView>

        {/* GPS Lock */}
        <BlurView style={styles.gpsGlass} blurType="light" blurAmount={20}>
          <Text style={styles.gpsLabel}>QUANTUM LOCK</Text>
          <Text style={styles.coords}>{coords}</Text>
        </BlurView>

        {/* Quantum Risk Wheel */}
        <View style={styles.wheelContainer}>
          <Animated.View style={[styles.outerRing, { transform: [{ rotate: spin }], opacity: glowValue }]}>
            <LinearGradient colors={getVerdictColor()} style={StyleSheet.absoluteFill} />
          </Animated.View>

          <View style={styles.wheel}>
            <BlurView style={styles.wheelGlass} blurType="dark" blurAmount={15}>
              <View style={[styles.innerCore, { backgroundColor: result ? getVerdictColor()[0] : '#1a0033' }]} />
            </BlurView>
          </View>

          {/* Particle field */}
          {[...Array(12)].map((_, i) => (
            <Animated.View
              key={i}
              style={[
                styles.particle,
                {
                  transform: [
                    { translateX: 100 * Math.cos(i * 30 * Math.PI / 180) },
                    { translateY: 100 * Math.sin(i * 30 * Math.PI / 180) },
                  ],
                  opacity: glowValue,
                },
              ]}
            />
          ))}
        </View>

        {/* Result */}
        <View style={styles.resultContainer}>
          <Text style={[styles.result, { color: result ? getVerdictColor()[0] : '#8b5cf6' }]}>
            {result || 'AWAITING VERDICT'}
          </Text>
          <Text style={styles.entropy}>{entropy}</Text>
        </View>

        {/* Scan Button */}
        <TouchableOpacity
          style={[styles.scanButton, scanning && styles.scanning]}
          onPress={startScanning}
          disabled={scanning}
          activeOpacity={0.8}
        >
          <LinearGradient
            colors={scanning ? ['#333', '#555'] : ['#8b5cf6', '#ec4899']}
            style={styles.gradientButton}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <BlurView style={styles.buttonGlass} blurType="dark" blurAmount={20}>
              <Text style={styles.scanText}>
                {scanning ? 'SCANNING QUANTUM FIELD...' : 'INITIATE QUANTUM SCAN'}
              </Text>
            </BlurView>
          </LinearGradient>
        </TouchableOpacity>

        {/* Status bar glow */}
        <Animated.View style={[styles.bottomGlow, { opacity: glowValue }]} />
      </SafeAreaView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: { flex: 1, backgroundColor: '#000' },
  container: { flex: 1, alignItems: 'center', paddingTop: 40 },
  
  headerGlass: {
    padding: 30,
    borderRadius: 30,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)',
    backgroundColor: 'rgba(20, 0, 40, 0.4)',
    marginBottom: 30,
  },
  title: { fontSize: 48, fontWeight: '900', textAlign: 'center', backgroundColor: 'transparent' },
  subtitle: { fontSize: 16, color: '#aaa', textAlign: 'center', marginTop: 8, opacity: 0.8 },

  gpsGlass: {
    paddingHorizontal: 30,
    paddingVertical: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 150, 0.3)',
    marginBottom: 40,
  },
  gpsLabel: { color: '#0f0', fontSize: 12, opacity: 0.8 },
  coords: { color: '#0ff', fontSize: 18, fontWeight: 'bold', marginTop: 8 },

  wheelContainer: { position: 'relative', width: 300, height: 300, justifyContent: 'center', alignItems: 'center' },
  outerRing: {
    position: 'absolute',
    width: 340,
    height: 340,
    borderRadius: 170,
    borderWidth: 8,
  },
  wheel: {
    width: 260,
    height: 260,
    borderRadius: 130,
    overflow: 'hidden',
    borderWidth: 3,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  wheelGlass: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  innerCore: {
    width: 180,
    height: 180,
    borderRadius: 90,
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 20,
    elevation: 20,
  },
  particle: {
    position: 'absolute',
    width: 8,
    height: 8,
    backgroundColor: '#8b5cf6',
    borderRadius: 4,
    shadowColor: '#8b5cf6',
    shadowRadius: 10,
    shadowOpacity: 0.8,
  },

  resultContainer: { marginTop: 50, alignItems: 'center' },
  result: { fontSize: 52, fontWeight: '900', textShadowColor: 'rgba(139, 92, 246, 0.8)', textShadowRadius: 20 },
  entropy: { color: '#aaa', fontSize: 16, marginTop: 10, opacity: 0.9 },

  scanButton: { marginTop: 50, borderRadius: 25, overflow: 'hidden' },
  scanning: { opacity: 0.7 },
  gradientButton: { padding: 2 },
  buttonGlass: {
    paddingHorizontal: 50,
    paddingVertical: 22,
    alignItems: 'center',
  },
  scanText: { color: '#fff', fontSize: 20, fontWeight: 'bold', letterSpacing: 2 },

  bottomGlow: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 200,
    backgroundColor: '#8b5cf6',
    opacity: 0.1,
    blurRadius: 100,
  },
});

export default QRSApp;
