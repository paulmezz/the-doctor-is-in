
echo "run these"

for i in $(grep ^[a-Z] ../etc/children.yaml | cut -d : -f 2-3 | sed s-http://--g) ; do
	echo sudo rsync -avHh --progress --rsh="ssh" /var/lib/bluetooth/* $i:/var/lib/bluetooth/
	echo sudo ssh $i systemctl restart bluetooth.service
done
