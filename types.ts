
export interface CarbonData {
  month: string;
  transport: number;
  electricity: number;
  food: number;
  total: number;
}

export interface EstimateInputs {
  bodyType: 'overweight' | 'obese' | 'underweight' | 'normal';
  sex: 'female' | 'male';
  diet: 'pescatarian' | 'vegetarian' | 'omnivore' | 'vegan';
  howOftenShower: 'daily' | 'less frequently' | 'more frequently' | 'twice a day';
  heatingEnergySource: 'coal' | 'natural gas' | 'wood' | 'electricity';
  transport: 'public' | 'walk/bicycle' | 'private';
  vehicleType: 'petrol' | 'diesel' | 'hybrid' | 'lpg' | 'electric' | '';
  socialActivity: 'often' | 'sometimes' | 'never';
  monthlyGroceryBill: number;
  frequencyOfTravelingByAir: 'frequently' | 'rarely' | 'never' | 'very frequently';
  vehicleMonthlyDistanceKm: number;
  wasteBagSize: 'large' | 'extra large' | 'small' | 'medium';
  wasteBagWeeklyCount: number;
  howLongTVPCDailyHour: number;
  howManyNewClothesMonthly: number;
  howLongInternetDailyHour: number;
  energyEfficiency: 'No' | 'Sometimes' | 'Yes';
  recycling: string[]; // ['Paper', 'Plastic', 'Glass', 'Metal']
  cookingWith: string[]; // ['Stove', 'Oven', 'Microwave', 'Grill', 'Airfryer']
}

export interface EstimateResult {
  totalKgCO2: number;
  breakdown: {
    transport: number;
    energy: number;
    food: number;
    waste: number;
  };
  aiAnalysis: string;
  confidenceScore: number;
}

export interface PickAction {
  id: string;
  title: string;
  description: string;
  co2SavedKg: number;
  imageUrl: string;
  category: 'transport' | 'energy' | 'food' | 'lifestyle';
}

export interface UserSettings {
  theme: 'light' | 'dark';
  reducedMotion: boolean;
  animationSpeed: number; // Multiplier, 1 = normal
  units: 'kg' | 'ton';
}

export type ViewState = 'dashboard' | 'estimate' | 'picks' | 'settings';
