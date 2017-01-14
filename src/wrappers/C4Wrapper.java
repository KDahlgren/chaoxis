//package edu.berkeley.cs.boom.molly.wrappers

import edu.berkeley.cs.boom.molly.UltimateModel
import jnr.ffi.LibraryLoader

class C4Wrapper(name: String, program: Program)
               (implicit val metricRegistry: MetricRegistry)  extends LazyLogging with InstrumentedBuilder {

  private val time = metrics.timer("time")

  def run: UltimateModel = C4Wrapper.synchronized {
    time.time {
      C4Wrapper.libC4.c4_initialize()
      val c4 = C4Wrapper.libC4.c4_make(null, 0)
      try {
        // Install the clock facts one timestep at a time in order to stratify the
        // execution by time:
        val (clockFacts, nonClockFacts) = program.facts.partition(_.tableName == "clock")
        val rulesPlusNonClockFacts = C4CodeGenerator.generate(program.copy(facts=nonClockFacts))
        logger.debug("C4 input minus clock facts is:\n" + rulesPlusNonClockFacts)
        assert(C4Wrapper.libC4.c4_install_str(c4, rulesPlusNonClockFacts) == 0)
        val clockFactsByTime = clockFacts.groupBy(_.cols(2).asInstanceOf[IntLiteral].int)
        for ((time, facts) <- clockFactsByTime.toSeq.sortBy(_._1)) {
          val clockFactsProgram = C4CodeGenerator.generate(new Program(Nil, facts, Nil))
          logger.debug(s"Installing clock facts for time $time:\n$clockFactsProgram")
          assert(C4Wrapper.libC4.c4_install_str(c4, clockFactsProgram) == 0)
        }
        val tables = program.tables.map {
          t => (t.name, parseTableDump(C4Wrapper.libC4.c4_dump_table(c4, t.name)))
        }.toMap
        new UltimateModel(tables)
      } finally {
        C4Wrapper.libC4.c4_destroy(c4)
        C4Wrapper.libC4.c4_terminate()
      }
    }
  }

  def parseTableDump(string: String): List[List[String]] = {
    string.lines.map(_.split(",").toList).toList
  }
}

object C4Wrapper {
  val libC4: C4 = LibraryLoader.create(classOf[C4]).load("c4")
}
