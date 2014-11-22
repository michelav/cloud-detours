package br.unifor.ppgia.cloud.detours.io;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import br.unifor.ppgia.cloud.core.CloudDetoursException;
import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider.EventType;
import br.unifor.ppgia.cloud.core.comm.Event;

public class SimpleDetouredFile extends File {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	private static final Logger logger = Logger
			.getLogger(SimpleDetouredFile.class.getName());

	private Channel channel;

	private String objectName;

	private ChannelProvider provider;

	public SimpleDetouredFile(File parent, String child) {
		super(parent, child);
		try {
			objectName = super.getCanonicalPath();
		} catch (IOException e) {
			String errorMsg = String.format(
					"Fatal error: Could not parse arguments: %s and %s",
					parent.getPath(), child);
			logger.log(Level.SEVERE, errorMsg);
			throw new CloudDetoursException(errorMsg);
		}
		provider = ChannelProvider.getInstance();
	}

	public SimpleDetouredFile(String pathname) {
		super(pathname);
		objectName = pathname;
		provider = ChannelProvider.getInstance();
	}

	public void configureChannel(Channel theChannel) {
		this.channel = theChannel;
	}

	@Override
	public boolean exists() {
		Event existsEvent = provider.getEvent(EventType.EXISTS_EVT);
		existsEvent.addInfo("obj_name", objectName);
		channel.sendEvent(existsEvent);
		Event recvEvent = channel.recvEvent();
		return parseReturn(recvEvent);
	}

	@Override
	public boolean mkdir() {
		Event mkDirReq = provider.getEvent(EventType.MKDIR_EVT);
		mkDirReq.addInfo("dir_name", objectName);

		channel.sendEvent(mkDirReq);
		Event recvEvent = channel.recvEvent();
		return parseReturn(recvEvent);
	}

	private boolean parseReturn(Event returned) {
		if (returned == null) {
			String msg = "Fatal error: Null event.";
			logger.log(Level.SEVERE, msg);
			throw new CloudDetoursException(msg);
		}

		String errorType = returned.getInfo("error");
		if (errorType != null) {
			String message = returned.getInfo("message");
			StringBuffer errorMessage = new StringBuffer(errorType);
			errorMessage.append(": ").append(message);
			logger.log(Level.SEVERE, errorMessage.toString());
			return false;
		} else {
			String evtReturn = returned.getInfo("return");
			return "True".equalsIgnoreCase(evtReturn);
		}
	}
}
