/*
 * Adapted from React Bits FadeContent by David Haz.
 * MIT + Commons Clause License Condition v1.0 — see docs/design/third-party-ui.md.
 */
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useEffect, useRef, type HTMLAttributes, type ReactNode } from 'react'

gsap.registerPlugin(ScrollTrigger)

type FadeContentProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode
  duration?: number
  delay?: number
  threshold?: number
}

export function FadeContent({ children, duration = 0.55, delay = 0, threshold = 0.08, className = '', ...props }: FadeContentProps) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const element = ref.current
    if (!element || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    gsap.set(element, { autoAlpha: 0, y: 12 })
    const tween = gsap.to(element, { autoAlpha: 1, y: 0, duration, delay, ease: 'power2.out', paused: true })
    const trigger = ScrollTrigger.create({ trigger: element, start: `top ${(1 - threshold) * 100}%`, once: true, onEnter: () => tween.play() })
    return () => { trigger.kill(); tween.kill() }
  }, [delay, duration, threshold])
  return <div ref={ref} className={className} {...props}>{children}</div>
}
