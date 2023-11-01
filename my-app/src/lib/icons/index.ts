import type { Icon as LucideIcon } from "lucide-svelte";
import {
  AlertTriangle,
  AppWindow,
  ArrowBigRight,
  ArrowDown,
  ArrowRight,
  Bot,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ClipboardCheck,
  Copy,
  CreditCard,
  File,
  FileText,
  HardDrive,
  HelpCircle,
  Home,
  Image,
  Key,
  Laptop,
  Link,
  ListTree,
  Loader2,
  LogOut,
  Mail,
  MessageSquare,
  Moon,
  MoreHorizontal,
  MoreVertical,
  Pizza,
  Plus,
  RefreshCcw,
  Settings,
  Share,
  Sidebar,
  StopCircle,
  SunMedium,
  Trash,
  Twitter,
  User,
  Users,
  X,
} from "lucide-svelte";
import { Dashboard } from "radix-icons-svelte";

import Apple from "./apple.svelte";
import Aria from "./aria.svelte";
import Discord from "./discord.svelte";
import GitHub from "./github.svelte";
import Google from "./google.svelte";
import Logo from "./logo.svelte";
import Npm from "./npm.svelte";
import PayPal from "./paypal.svelte";
import Pnpm from "./pnpm.svelte";
import RadixSvelte from "./radix-svelte.svelte";
import Tailwind from "./tailwind.svelte";
import Yarn from "./yarn.svelte";
import Audi from "./audi.svelte";


export type Icon = LucideIcon;

export const Icons = {
  logo: Logo,
  close: X,
  spinner: Loader2,
  arrowElbow: ArrowBigRight,
  chevronLeft: ChevronLeft,
  plus: Plus,
  chevronRight: ChevronRight,
  chevronUp: ChevronUp,
  chevronDown: ChevronDown,
  trash: Trash,
  share: Share,
  post: FileText,
  page: File,
  media: Image,
  settings: Settings,
  home: Home,
  link: Link,
  billing: CreditCard,
  ellipsis: MoreVertical,
  applications: AppWindow,
  dotsHorizontal: MoreHorizontal,
  dashboard: Dashboard,
  indexes: ListTree,
  dataSources: HardDrive,
  sidebar: Sidebar,
  add: Plus,
  users: Users,
  message: MessageSquare,
  warning: AlertTriangle,
  user: User,
  ai: Bot,
  refresh: RefreshCcw,
  stop: StopCircle,
  arrowRight: ArrowRight,
  arrowDown: ArrowDown,
  help: HelpCircle,
  pizza: Pizza,
  twitter: Twitter,
  check: Check,
  copy: Copy,
  copyDone: ClipboardCheck,
  sun: SunMedium,
  moon: Moon,
  laptop: Laptop,
  gitHub: GitHub,
  radix: RadixSvelte,
  aria: Aria,
  npm: Npm,
  yarn: Yarn,
  pnpm: Pnpm,
  tailwind: Tailwind,
  google: Google,
  apple: Apple,
  paypal: PayPal,
  logout: LogOut,
  discord: Discord,
  key: Key,
  mail: Mail,
  audi: Audi,
};
