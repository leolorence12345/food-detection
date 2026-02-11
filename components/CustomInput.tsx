import React from "react";
import { TextInput } from "react-native-paper";
import { customTheme } from "../constants/themeConstants";

interface CustomInputProps {
  maxLength?: number;
  placeholder: string;
  isSecureTextEntry?: boolean;
  keyboardType?: "default" | "numeric" | "email-address" | "phone-pad";
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  onChangeText: (text: string) => void;
  value: string | number;
  error?: boolean | string;
  isDisabled?: boolean;
  onFocus?: () => void;
  onSubmitEditing?: () => void;
  returnKeyType?: "done" | "go" | "next" | "search" | "send";
  blurOnSubmit?: boolean;
}

const CustomInput = React.forwardRef<any, CustomInputProps>(({
  maxLength,
  placeholder,
  isSecureTextEntry,
  keyboardType = "default",
  autoCapitalize = "sentences",
  onChangeText,
  value,
  error,
  isDisabled,
  onFocus,
  onSubmitEditing,
  returnKeyType = "done",
  blurOnSubmit = true,
}, ref) => {
  return (
    <TextInput
      ref={ref}
      label={placeholder}
      keyboardType={keyboardType}
      autoCapitalize={autoCapitalize}
      secureTextEntry={isSecureTextEntry}
      onChangeText={onChangeText}
      onFocus={onFocus}
      onSubmitEditing={onSubmitEditing || (() => {})}
      returnKeyType={returnKeyType}
      value={value ? value.toString() : ""}
      editable={!isDisabled}
      focusable={!isDisabled}
      blurOnSubmit={blurOnSubmit}
      maxLength={maxLength}
      mode="outlined"
      dense={false}
      outlineColor={
        isDisabled
          ? customTheme.colors.darkSecondary
          : customTheme.colors.dark
      }
      placeholderTextColor={
        isDisabled
          ? customTheme.colors.darkSecondary
          : customTheme.colors.dark
      }
      contentStyle={{
        color: isDisabled
          ? customTheme.colors.darkSecondary
          : customTheme.colors.dark,
      }}
      style={{
        height: 55,
        backgroundColor: customTheme.colors.light,
        fontSize: 16,
        marginBottom: 4,
      }}
      theme={{
        colors: {
          primary: customTheme.colors.primary,
          error: "#E32A17",
        },
      }}
      error={!!error}
    />
  );
});

CustomInput.displayName = 'CustomInput';

export default CustomInput;

