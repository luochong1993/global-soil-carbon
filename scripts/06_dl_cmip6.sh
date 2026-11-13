cd /workspace/soil_global/data/cmip6
for g in ACCESS-CM2 EC-Earth3-Veg MPI-ESM1-2-HR UKESM1-0-LL IPSL-CM6A-LR MIROC6; do for s in 126 245 370 585; do for p in 2041-2060 2081-2100; do for v in tmin tmax prec bioc; do echo "$g $s $p $v"; done; done; done; done | xargs -P 8 -n 4 sh -c 'f=wc2.1_10m_$4_$1_ssp$2_$3.tif; [ -s $f ] || curl -sfL -m 900 -o $f.part https://geodata.ucdavis.edu/cmip6/10m/$1/ssp$2/$f && mv $f.part $f || echo FAIL $f' _
echo ALLDONE
