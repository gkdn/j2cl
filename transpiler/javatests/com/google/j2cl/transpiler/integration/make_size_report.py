#!/usr/bin/python2.7
#
# Copyright 2015 Google Inc. All Rights Reserved.

"""Reports optimized size changes caused by the current CL."""


import getpass
import os
import time


import repo_util


def find_last_stats(stat_lines, synced_to_cl):
  """Returns the opt size in the highest CL before the current sync cl."""
  last_optimized_size = 0

  for stat_line in stat_lines:
    cl, optimized_size = stat_line.split("\t")
    cl = int(cl)
    optimized_size = int(optimized_size)

    if cl > synced_to_cl:
      break
    else:
      last_optimized_size = optimized_size

  return last_optimized_size


def make_size_report():
  """Compare current test sizes and generate a report."""
  size_report_file = open(
      os.path.join(
          os.path.dirname(__file__), "size_report.txt"),
      "w+")

  repo_util.build_optimized_tests()

  synced_to_cl = repo_util.compute_synced_to_cl()

  size_report_file.write("Integration tests optimized size report:\n")
  size_report_file.write("**************************************\n")
  size_report_file.write("Generated by %s at %s.\n" %
                         (getpass.getuser(), time.strftime("%c")))

  size_report_file.write("Synced @%s.\n" % synced_to_cl)

  print "  Comparing sizes."
  last_total_size = 0
  total_size = 0
  all_reports = []
  new_reports = []
  shrinkage_reports = []
  expansion_reports = []
  optimized_size_change_count = 0
  for (test_name, js_file) in repo_util.get_js_files_by_test_name():
    optimized_size = os.path.getsize(js_file)
    optimized_size_log_path = (
        repo_util.managed_repo_compute_test_size_path(test_name))

    if os.path.isfile(optimized_size_log_path):
      # compare old and new size
      optimized_size_log_file = open(optimized_size_log_path, "r")

      last_optimized_size = find_last_stats(
          optimized_size_log_file.readlines(), synced_to_cl)

      # This can only happen if you have synced back in time such that the
      # optimized size cache does already contain a file for your new
      # tests but that file does not contain any entries older than the
      # cl at which you are synced.
      if last_optimized_size == 0:
        # record initial size
        optimized_size_change_count += 1
        message = "  '%s' is %s bytes\n" % (test_name, optimized_size)
        all_reports.append(message)
        new_reports.append(message)
        continue

      last_total_size += last_optimized_size
      total_size += optimized_size

      if optimized_size > last_optimized_size:
        optimized_size_change_count += 1
        increased_percent = (
            optimized_size / float(last_optimized_size) - 1) * 100
        message = (
            "  '%s' %s->%s bytes (+%2.2f%%)\n" %
            (test_name, last_optimized_size, optimized_size,
             increased_percent))
        all_reports.append(message)
        expansion_reports.append((increased_percent, message))
      elif optimized_size < last_optimized_size:
        optimized_size_change_count += 1
        decreased_percent = (
            1 - optimized_size / float(last_optimized_size)) * 100
        message = ("  '%s' %s->%s bytes (-%2.2f%%)\n" %
                   (test_name, last_optimized_size, optimized_size,
                    decreased_percent))
        all_reports.append(message)
        shrinkage_reports.append((decreased_percent, message))
      else:
        message = ("  '%s' %s bytes (unchanged)\n" %
                   (test_name, optimized_size))
        all_reports.append(message)
    else:
      # record initial size
      optimized_size_change_count += 1
      message = "  '%s' is %s bytes\n" % (test_name, optimized_size)
      all_reports.append(message)
      new_reports.append(message)

  # Keep a maximum of 4 of the largest shrinkages.
  shrinkage_reports = (
      sorted(shrinkage_reports, key=lambda report: report[0], reverse=True)
      [0: 4])
  # Keep a maximum of 4 of the largest expansions.
  expansion_reports = (
      sorted(expansion_reports, key=lambda report: report[0], reverse=False)
      [0: 4])

  size_report_file.write(
      "There are %s size changes.\n" % optimized_size_change_count)

  if total_size != last_total_size:
    total_percent = (
        total_size / float(last_total_size)) * 100
    size_report_file.write(
        "Total size (of already existing tests) "
        "changed from %s to %s bytes (100%%->%2.2f%%).\n" %
        (last_total_size, total_size, total_percent))
  else:
    size_report_file.write(
        "Total size (of already existing tests) did not change.\n")

  size_report_file.write("\n")
  size_report_file.write("\n")
  size_report_file.write("New reports:\n")
  size_report_file.write("**************************************\n")
  if new_reports:
    for new_report in new_reports:
      size_report_file.write(new_report)
  else:
    size_report_file.write("  none\n")

  size_report_file.write("\n")
  size_report_file.write("\n")
  size_report_file.write("Shrinkage report highlights:\n")
  size_report_file.write("**************************************\n")
  if shrinkage_reports:
    for shrinkage_report in shrinkage_reports:
      size_report_file.write(shrinkage_report[1])
  else:
    size_report_file.write("  none\n")

  size_report_file.write("\n")
  size_report_file.write("\n")
  size_report_file.write("Expansion report highlights:\n")
  size_report_file.write("**************************************\n")
  if expansion_reports:
    for expansion_report in expansion_reports:
      size_report_file.write(expansion_report[1])
  else:
    size_report_file.write("  none\n")

  size_report_file.write("\n")
  size_report_file.write("\n")
  size_report_file.write("All reports:\n")
  size_report_file.write("**************************************\n")
  if all_reports:
    for all_report in all_reports:
      size_report_file.write(all_report)
  else:
    size_report_file.write("  none\n")
  size_report_file.close()
  print "  Closing report (%s)" % size_report_file.name


def main():
  print "Generating the size change report:"

  repo_util.managed_repo_validate_environment()
  repo_util.managed_repo_update_sizes_cache()
  make_size_report()


main()
