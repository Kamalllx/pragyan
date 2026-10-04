import { Composer } from "@/components/Composer";
import { FilmGrid } from "@/components/FilmGrid";

export default function Studio() {
  return (
    <div className="mx-auto max-w-[1120px] px-4 sm:px-6">
      <section className="pt-16 pb-14 sm:pt-24">
        <h1 className="max-w-[16ch] font-display text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] font-semibold tracking-[-0.035em] text-balance">
          What should Pragyan explain?
        </h1>
        <p className="mt-5 max-w-[60ch] text-[17px] leading-relaxed text-ash">
          Give it a question, a problem, a photo of your homework or your project notes. A team of local agents works out what you need, solves and checks
          it, writes the storyboard, narrates, animates and renders a finished video — all on this machine.
        </p>
        <div className="mt-10">
          <Composer />
        </div>
      </section>
      <div className="pb-24">
        <FilmGrid limit={6} />
      </div>
    </div>
  );
}
