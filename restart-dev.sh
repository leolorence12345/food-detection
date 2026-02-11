#!/bin/bash
echo "Stopping any running Metro processes..."
pkill -f "react-native|metro" || true

echo "Clearing Metro cache..."
rm -rf $TMPDIR/metro-* || true
rm -rf $TMPDIR/react-* || true

echo "Clearing watchman..."
watchman watch-del-all 2>/dev/null || true

echo "Clearing npm cache..."
npm cache clean --force

echo "Restarting with clean cache..."
npx expo start --clear
