import React, { useState, useEffect, useMemo } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Image,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
  TouchableWithoutFeedback,
  Keyboard,
} from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import VectorBackButton from '../components/VectorBackButton';
import CustomButton from '../components/CustomButton';
import BottomButtonContainer from '../components/BottomButtonContainer';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setAvatar, updateProfileFields, loadProfile } from '../store/slices/profileSlice';
import { avatarList, Avatar } from '../constants/avatarConstants';

export default function AddAvatarScreen() {
  const insets = useSafeAreaInsets();
  const navigation = useNavigation();
  const route = useRoute();
  const dispatch = useAppDispatch();
  const profileState = useAppSelector((state) => state.profile);
  const [selectedAvatar, setSelectedAvatar] = useState<Avatar | null>(null);
  
  // Hermes-safe param reading - never mutate route.params
  const { fromBusinessProfile = false, fromProfile = false, fromEditProfile = false } = 
    (route.params ?? {}) as { 
      fromBusinessProfile?: boolean; 
      fromProfile?: boolean; 
      fromEditProfile?: boolean;
    };
  const isFromBusinessProfile = fromBusinessProfile === true;
  
  // Calculate bottom padding for FlatList to account for button container
  // Button height (56) + container padding top (16) + container padding bottom (16) + border (1)
  const buttonContainerHeight = 56 + 16 + 16 + 1;

  // Load avatar on mount
  useEffect(() => {
    let isMounted = true;
    
    const loadCurrentAvatar = async () => {
      try {
        if (isFromBusinessProfile) {
          // Load from temporary step1 data
          try {
            const savedData = await AsyncStorage.getItem('business_profile_step1');
            if (savedData && isMounted) {
              const data = JSON.parse(savedData);
              if (data.avatar) {
                setSelectedAvatar(data.avatar);
              }
            }
          } catch (error) {
            console.error('[AddAvatar] Error loading avatar from step1:', error);
          }
        } else {
          // Load from Redux profile state
          if (profileState.avatar && isMounted) {
            setSelectedAvatar(profileState.avatar);
          } else if (!profileState.avatar && !profileState.isLoading && !profileState.businessProfile && !profileState.userAccount && isMounted) {
            // Only load profile if:
            // 1. No avatar in state
            // 2. Not currently loading
            // 3. Profile hasn't been loaded yet (no businessProfile or userAccount)
            // This prevents triggering AppLoader when profile is already loaded
            try {
              await dispatch(loadProfile()).unwrap();
              // Note: profileState.avatar will be updated by Redux, handled in next effect
            } catch (error) {
              console.error('[AddAvatar] Error loading profile:', error);
              // Continue even if loadProfile fails - user can still select an avatar
            }
          }
          // If profile is loaded but avatar is missing, user can still select an avatar
          // Don't call loadProfile() to avoid triggering AppLoader
        }
      } catch (error) {
        console.error('[AddAvatar] Unexpected error in loadCurrentAvatar:', error);
      }
    };
    
    loadCurrentAvatar();
    
    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isFromBusinessProfile]);
  
  // Update avatar when profileState.avatar changes (e.g., after loadProfile completes)
  useEffect(() => {
    if (!isFromBusinessProfile && profileState.avatar && !selectedAvatar) {
      setSelectedAvatar(profileState.avatar);
    }
  }, [isFromBusinessProfile, profileState.avatar, selectedAvatar]);

  const saveAvatar = async () => {
    if (!selectedAvatar) {
      return;
    }

    if (isFromBusinessProfile) {
      // Save to temporary step1 data
      try {
        const savedData = await AsyncStorage.getItem('business_profile_step1');
        const data = savedData ? JSON.parse(savedData) : {};
        data.avatar = selectedAvatar;
        await AsyncStorage.setItem('business_profile_step1', JSON.stringify(data));
        navigation.goBack();
      } catch (error) {
        console.error('Error saving avatar to step1:', error);
      }
    } else {
      // Save to user account via Redux
      const result = await dispatch(setAvatar(selectedAvatar));
      if (setAvatar.fulfilled.match(result)) {
        // Clear profile image if avatar is selected
        await dispatch(updateProfileFields({ profileImage: undefined }));
        navigation.goBack();
      }
    }
  };

  // Group avatars into rows of 3 for grid layout
  const avatarRows = useMemo(() => {
    const rows: Avatar[][] = [];
    for (let i = 0; i < avatarList.length; i += 3) {
      rows.push(avatarList.slice(i, i + 3));
    }
    return rows;
  }, []);

  const isIOS = Platform.OS === 'ios';

  const Content = (
    <TouchableWithoutFeedback onPress={() => Keyboard.dismiss()}>
      <View style={styles.contentWrapper}>
        {/* Header */}
        <View style={styles.header}>
          <VectorBackButton onPress={() => navigation.goBack()} />
          <Text style={styles.headerTitle}>Add Avatar</Text>
          <View style={{ width: 40 }} />
        </View>

        {/* Avatars Grid */}
        <View style={styles.content}>
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={[styles.avatarList, { paddingBottom: buttonContainerHeight + 20 }]}
            showsVerticalScrollIndicator={false}
          >
            {avatarRows.map((row, rowIndex) => (
              <View key={rowIndex} style={styles.row}>
                {row.map((avatar) => {
                  const isSelected = selectedAvatar?.id === avatar.id;
                  return (
                    <View
                      key={avatar.id}
                      style={[
                        styles.avatarContainer,
                        isSelected && styles.avatarContainerSelected,
                      ]}
                    >
                      <TouchableOpacity
                        onPress={() => setSelectedAvatar(avatar)}
                        activeOpacity={0.7}
                      >
                        <Image source={avatar.imgSrc} style={styles.avatarImage} />
                      </TouchableOpacity>
                    </View>
                  );
                })}
                {/* Fill remaining columns if row has less than 3 items */}
                {row.length < 3 && Array.from({ length: 3 - row.length }).map((_, idx) => (
                  <View key={`spacer-${idx}`} style={styles.spacer} />
                ))}
              </View>
            ))}
          </ScrollView>
        </View>
      </View>
    </TouchableWithoutFeedback>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      {isIOS ? (
        <KeyboardAvoidingView
          behavior="padding"
          style={{ flex: 1 }}
          keyboardVerticalOffset={insets.top}
        >
          {Content}
        </KeyboardAvoidingView>
      ) : (
        <View style={{ flex: 1 }}>
          {Content}
        </View>
      )}
      {/* Save Button - Fixed at Bottom (outside flex container to stay fixed) */}
      <BottomButtonContainer>
        <CustomButton
          variant="primary"
          btnLabel="Save"
          onPress={saveAvatar}
          disabled={!selectedAvatar}
        />
      </BottomButtonContainer>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    position: 'relative',
  },
  contentWrapper: {
    flex: 1,
    flexDirection: 'column',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 2,
    borderBottomColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000000',
    flex: 1,
    marginLeft: 12,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  scrollView: {
    flex: 1,
  },
  avatarList: {
    alignItems: 'center',
    justifyContent: 'center',
    flexGrow: 1,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#F3F4F6',
    margin: 8,
    padding: 5,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarContainerSelected: {
    borderColor: '#7BA21B',
    borderWidth: 3,
  },
  avatarImage: {
    width: 70,
    height: 70,
    borderRadius: 35,
  },
  spacer: {
    width: 100,
    height: 100,
    margin: 8,
  },
});

