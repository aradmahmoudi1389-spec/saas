import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import { brands, type Brand } from "../data"

export type UserSession = {
  phone: string
  firstName: string
  role: "USER" | "ADMIN" | "SUPER_ADMIN"
}
export type AppState = {
  session: UserSession | null
  activeBrand: Brand
  brands: Brand[]
  freePostsUsed: number
  setSession: (session: UserSession | null) => void
  setActiveBrand: (brand: Brand) => void
  addBrand: (brand: Brand) => void
  incrementFreePosts: () => void
}

const AppContext = createContext<AppState | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<UserSession | null>(null)
  const [brandList, setBrandList] = useState(brands)
  const [activeBrand, setActiveBrand] = useState(brands[0])
  const [freePostsUsed, setFreePostsUsed] = useState(2)
  const value = useMemo<AppState>(
    () => ({
      session,
      activeBrand,
      brands: brandList,
      freePostsUsed,
      setSession,
      setActiveBrand,
      addBrand: (brand) => {
        setBrandList((current) => [...current, brand])
        setActiveBrand(brand)
      },
      incrementFreePosts: () =>
        setFreePostsUsed((current) => Math.min(5, current + 1)),
    }),
    [activeBrand, brandList, freePostsUsed, session],
  )
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useAppState() {
  const context = useContext(AppContext)
  if (!context) throw new Error("useAppState must be used inside AppProvider")
  return context
}
