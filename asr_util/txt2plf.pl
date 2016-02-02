#!/usr/bin/env perl

# Converts AT&T FSMs (in text format) to Chris Dyer's PLF format.

use strict;
use warnings;

binmode(STDIN,  ":utf8");
binmode(STDOUT, ":utf8");

# End states may be marked with a final weight, which we need to add to all arcs ending in that
# state.
my %endweights;
my @arcs;
while (<>) {
  chomp();
  # print STDERR "LINE($_)\n";

  my @tokens = split('\t', $_);
  my ($i,$j,undef,$label,$score) = @tokens;
  if (@tokens == 2) {
    # end state
    $endweights{$i} = $j;
    next;
  } elsif (@tokens < 4) {
    next;
  }

  #$label = lc $label;
  $label =~ s/^\*//;
  $score = 0.0 unless defined $score;

  if (defined $j) {
    if ($j < $i) {
      print "* [$.] FATAL: $j < $i\n";
      #exit;
    }
    push @{$arcs[$i][$j-$i]}, [$label,$score];
  }
}

print "(";
foreach my $i (0..$#arcs) {
  next unless defined $arcs[$i];
  print "(";
  foreach my $j (0..$#{$arcs[$i]}) {
    next unless defined $arcs[$i][$j];
    foreach my $arc (@{$arcs[$i][$j]}) {
      my ($label,$score) = @$arc;
      # add in the end weight if any
      if (exists $endweights{$i + $j}) {
        $score += $endweights{$i + $j};
      }
      $score *= -1;
      print "('".escape($label)."', $score, $j),";
    }
  }
  print "),";
}
print ")\n";

sub escape {
  my $arg = shift;
  $arg =~ s/'/\\'/g;
  return $arg;
}
