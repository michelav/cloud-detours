package br.unifor.ppgia.cloud.detours.io;

import static br.unifor.ppgia.cloud.core.comm.ChannelProvider._DETOURS_ENDPOINT_;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import net.javacoding.jspider.JSpider;
import net.javacoding.jspider.mod.plugin.diskwriter.DiskWriterPlugin;
import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider;

public aspect JSpiderIODetour extends AbstractIODetour {

	private Map<Thread, Channel> threadMap = new HashMap<Thread, Channel>();

	private static final Logger logger = Logger.getLogger("JSpiderIODetour");

	// XXX -> Won't be needed: withincode(public void
	// DiskWriterPlugin.ensureFolder(..))

	pointcut outputStreamAdaptationPoint():
		within(DiskWriterPlugin) && withincode(* writeFile(..));

	pointcut fileAdaptationPoint():
		within(DiskWriterPlugin) && withincode(* ensureFolder(..));

	
	pointcut freeResourcesPoint():
		execution(public void JSpider.start()) && within(net.javacoding.jspider.*);

	@Override
	public void allocateResources() {
		Thread currentThread = Thread.currentThread();
		Channel channel = threadMap.get(currentThread);
		if (channel == null) {
			ChannelProvider provider = ChannelProvider.getInstance();
			String endpoint = System.getenv(_DETOURS_ENDPOINT_);
			channel = provider.createChannel(endpoint);
			channel.connect();
			logger.log(Level.FINEST,
					"Channel created and bound to {0} endpoint.", endpoint);
		}
		super.currentChannel = channel;
		logger.fine("Channel allocated.");

	}

	public void releaseResources() {
		Thread currentThread = Thread.currentThread();
		Channel channel = threadMap.remove(currentThread);
		if (channel != null) {
			channel.close();
		}
		if (threadMap.isEmpty()) {
			ChannelProvider.getInstance().releaseResources();
		}
	}
}
