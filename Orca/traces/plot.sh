 #! /bin/bash
 gnuplot -persist <<EOF
 set data style linespoints
 show timestamp
 set title "$1"
 set xlabel "time (seconds)"
 set ylabel "Segments (cwnd, ssthresh)"
 plot "$1" using 1:7 title "snd_cwnd", \\
      "$1" using 1:(\$8>=2147483647 ? 0 : \$8) title "snd_ssthresh"
 EOF


