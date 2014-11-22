package br.unifor.ppgia.cloud.detours.io;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider.EventType;
import br.unifor.ppgia.cloud.core.comm.Event;

public class DetouredFileOutputStream extends FileOutputStream {

	private Channel channel;
	
	private File theFile;
	
	private ByteArrayOutputStream buffer = new ByteArrayOutputStream();

	private static final Logger logger = Logger
			.getLogger(DetouredFileOutputStream.class.getName());

	private ChannelProvider provider;

	public DetouredFileOutputStream(File file) throws FileNotFoundException {
		super(file);
		theFile = file;
		provider = ChannelProvider.getInstance();
	}

	@Override
	public void write(int b) throws IOException {
		buffer.write(b);
	}

	@Override
	public void close() throws IOException {
		flush();
		super.close();
	}

	@Override
	public void flush() throws IOException {
		byte[] payload = buffer.toByteArray();
		Event event = provider.getEvent(EventType.WRITE_EVT);
		event.addInfo("obj_name", theFile.getCanonicalPath());
		event.setPayload(payload);
		channel.sendEvent(event);
		Event recvEvent = channel.recvEvent();
		String errorType = recvEvent.getInfo("error");
		if(errorType != null) {
			String message = recvEvent.getInfo("message");
			StringBuffer errorMessage = new StringBuffer(errorType);
			errorMessage.append(": ").append(message);
			logger.log(Level.SEVERE, errorMessage.toString());
			throw new IOException(errorMessage.toString());
		}
	}

	public void configureChannel(Channel theChannel) {
		this.channel = theChannel;
	}

}
